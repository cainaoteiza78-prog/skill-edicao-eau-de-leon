"""
Passo 1 da edição: transcreve as takes (na ordem) com tempo por palavra.

Uso:
  python transcrever.py <pasta_trabalho> take1.mp4 take2.mp4 ... [--modelo small]

Gera em <pasta_trabalho>:
  transcricao.json   palavras com tempo (usado pelo render)
  transcricao.txt    leitura humana: cada fala com [take | início → fim]
  perfumes_citados.txt   perfumes do catálogo que parecem ter sido falados

Roda 100% local com faster-whisper (grátis, sem API paga). Na 1ª vez baixa o
modelo escolhido (~500 MB o "small", ~1,5 GB o "medium").
"""
import sys as _sys
_sys.stdout.reconfigure(encoding='utf-8', errors='replace')  # console do Windows
import argparse
import json
import os
import subprocess
import sys
import wave

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from catalogo import carregar, achar_citacoes  # noqa: E402

# Vocabulário que o Whisper erra em vídeo de perfumaria: vira contexto de grafia.
VOCABULARIO = (
    'Eau de Leon, decant, decants, perfume importado, perfumes importados, frasco, borrifada, '
    'fixação, projeção, rastro, notas de topo, coração, fundo, amadeirado, oriental, cítrico, '
    'baunilha, âmbar, almiscarado, Saiba mais, link da bio, cupom, frete grátis, Black Friday, '
    'Le Male, Elixir, Sauvage, Bleu de Chanel, Club de Nuit, Lattafa, Armaf, Creed Aventus, '
    'Invictus, One Million, 212 VIP, La Vie Est Belle, Good Girl, Yara, Khamrah, Asad, Xerjoff, '
    'Parfums de Marly, Layton, Baccarat Rouge, Orientica, Amber Rouge.'
)


def duracao(arq: str) -> float:
    r = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', arq],
        capture_output=True, text=True, check=True,
    )
    return float(r.stdout.strip())


def extrair_audio(arq: str, wav: str):
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', arq, '-vn', '-ac', '1', '-ar', '16000', wav], check=True)


# Palavras-chave que viram DESTAQUE 3D (o Claude confere e decide). A regra
# da oferta: QUANTO (10% DE DESCONTO), EM QUÊ (TODOS OS PERFUMES), ATÉ QUANDO
# (dia 10), e o CTA (SAIBA MAIS = botão). Ver treinamento/03.
ESCOPO = ['todos os perfumes', 'todo o site', 'site todo', 'site inteiro', 'loja toda', 'todos os decants',
          'frete gratis', 'primeira compra', 'kit descoberta', 'compre 1 leve 2', 'leve 3 pague 2']
CTA = ['saiba mais', 'link na bio', 'link da bio', 'clica aqui', 'clique aqui', 'chama no direct', 'compre agora']
FORTE = ['imperdivel', 'exclusivo', 'so hoje', 'ultimas unidades', 'acaba hoje', 'lancamento', 'gratis', 'gratuito']


def sugerir_destaques(saida, pasta):
    import re
    import unicodedata

    def n(s):
        s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
        return re.sub(r'[^a-z0-9%]+', ' ', s).strip()
    linhas = []
    for take in saida['takes']:
        pal = take['palavras']
        toks = [n(w['p']) for w in pal]

        def add(i, j, tipo):
            linhas.append(f"[take {take['n']} | {pal[i]['ini']:6.2f} → {pal[j]['fim']:6.2f}] {tipo:<10} "
                          + ' '.join(w['p'] for w in pal[i:j + 1]))
        i = 0
        while i < len(pal):
            achou = False
            # QUANTO: "10 %", "10%", "30 % de desconto", "R$ 50"
            num = re.fullmatch(r'\d+%?', toks[i] or '')
            if num:
                j = i
                if toks[i].endswith('%') or toks[i + 1:i + 2] == ['%']:
                    j = i if toks[i].endswith('%') else i + 1
                    if toks[j + 1:j + 3] == ['de', 'desconto'] or toks[j + 1:j + 3] == ['do', 'desconto']:
                        j += 2
                    add(i, j, 'QUANTO')
                    i, achou = j + 1, True
                elif i > 0 and toks[i - 1] in ('dia', 'ate'):
                    add(i - 1 if toks[i - 1] == 'dia' else i, i, 'ATE QUANDO')
                    i, achou = i + 1, True
            if not achou:
                for grupo, tipo in ((CTA, 'CTA-botao'), (ESCOPO, 'EM QUE'), (FORTE, 'FORTE')):
                    for c in sorted(grupo, key=len, reverse=True):
                        cs = c.split()
                        if toks[i:i + len(cs)] == cs:
                            add(i, i + len(cs) - 1, tipo)
                            i, achou = i + len(cs), True
                            break
                    if achou:
                        break
            if not achou:
                i += 1
    with open(os.path.join(pasta, 'destaques_sugeridos.txt'), 'w', encoding='utf8') as f:
        f.write('\n'.join(linhas) if linhas else 'Nenhuma palavra-chave da lista encontrada.')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('trabalho')
    ap.add_argument('takes', nargs='+')
    ap.add_argument('--modelo', default='small', help='tiny | base | small | medium | large-v3')
    a = ap.parse_args()

    from faster_whisper import WhisperModel

    os.makedirs(a.trabalho, exist_ok=True)
    modelo = WhisperModel(a.modelo, device='cpu', compute_type='int8')
    saida = {'takes': []}
    linhas = []
    for k, arq in enumerate(a.takes, 1):
        arq = os.path.abspath(arq)
        wav = os.path.join(a.trabalho, f'take{k}.wav')
        extrair_audio(arq, wav)
        # Passa o áudio já decodificado (evita depender do PyAV/ffmpeg interno).
        with wave.open(wav) as w:
            audio = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
        segs, _ = modelo.transcribe(
            audio, language='pt', word_timestamps=True, initial_prompt=VOCABULARIO,
            vad_filter=False, condition_on_previous_text=False,
        )
        palavras, falas = [], []
        for s in segs:
            falas.append({'ini': round(s.start, 2), 'fim': round(s.end, 2), 'texto': s.text.strip()})
            for w in s.words or []:
                if w.word.strip():
                    palavras.append({'p': w.word.strip(), 'ini': round(w.start, 3), 'fim': round(w.end, 3)})
        saida['takes'].append({'n': k, 'arquivo': arq, 'duracao': round(duracao(arq), 3), 'palavras': palavras, 'falas': falas})
        linhas.append(f'── TAKE {k}  ({os.path.basename(arq)}, {saida["takes"][-1]["duracao"]:.1f}s) ──')
        # Uma linha por FRASE (corta no . ? ! ou em pausa > 0,6 s), com o tempo
        # de cada palavra entre parênteses: é o que permite cortar um "corta,
        # vou de novo" no meio de um bloco longo.
        frase = []
        for i, w in enumerate(palavras):
            frase.append(w)
            prox = palavras[i + 1] if i + 1 < len(palavras) else None
            if prox is None or w['p'][-1:] in '.?!' or prox['ini'] - w['fim'] > 0.6:
                txt = ' '.join(x['p'] for x in frase)
                tempos = ' '.join(f"{x['p']}({x['ini']:.2f})" for x in frase)
                linhas.append(f"[take {k} | {frase[0]['ini']:6.2f} → {frase[-1]['fim']:6.2f}] {txt}")
                linhas.append(f'      ↳ {tempos}')
                frase = []
        linhas.append('')
        print(f'take {k}: {len(palavras)} palavras', flush=True)

    with open(os.path.join(a.trabalho, 'transcricao.json'), 'w', encoding='utf8') as f:
        json.dump(saida, f, ensure_ascii=False, indent=1)
    with open(os.path.join(a.trabalho, 'transcricao.txt'), 'w', encoding='utf8') as f:
        f.write('\n'.join(linhas))

    sugerir_destaques(saida, a.trabalho)
    cat = carregar()
    cit = achar_citacoes(saida, cat)
    with open(os.path.join(a.trabalho, 'perfumes_citados.txt'), 'w', encoding='utf8') as f:
        if not cit:
            f.write('Nenhum perfume do catálogo reconhecido na fala.\n')
        for c in cit:
            f.write(f'[take {c["take"]} | {c["ini"]:6.2f}] "{c["trecho"]}" → {c["id"]}  ({c["nome"]})\n')
    print(f'{len(cit)} citação(ões) de perfume encontradas. Arquivos em {a.trabalho}')


if __name__ == '__main__':
    main()
