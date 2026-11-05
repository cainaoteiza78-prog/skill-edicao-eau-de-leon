"""
Passo 4: tira quadros do vídeo editado e monta folhas de contato (PNG) pra
conferir com os olhos (o Claude abre o PNG com a ferramenta Read).

Uso:
  python conferir.py <video.mp4> [--cada 1.0] [--em 0.5,2.3,7.1] [--saida pasta]

Sem --em: um quadro a cada --cada segundos + os instantes de texto/perfume/b-roll
da linha_do_tempo.json (se existir ao lado do vídeo). Gera conferir_01.png,
conferir_02.png... com 8 quadros cada, tempo escrito em amarelo.
"""
import sys as _sys
_sys.stdout.reconfigure(encoding='utf-8', errors='replace')  # console do Windows
import argparse
import json
import os
import subprocess

from PIL import Image, ImageDraw


def quadro(video, t, destino):
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', f'{t:.3f}', '-i', video, '-frames:v', '1', '-vf', 'scale=270:480', destino], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('video')
    ap.add_argument('--cada', type=float, default=1.0)
    ap.add_argument('--em', default='')
    ap.add_argument('--saida', default='')
    a = ap.parse_args()
    video = os.path.abspath(a.video)
    pasta = a.saida or os.path.join(os.path.dirname(video), 'conferir')
    os.makedirs(pasta, exist_ok=True)
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', video],
                               capture_output=True, text=True).stdout)
    if a.em:
        tempos = [float(x) for x in a.em.split(',')]
    else:
        tempos = [round(x * a.cada, 2) for x in range(int(dur / a.cada) + 1)]
        lt = os.path.join(os.path.dirname(video), 'linha_do_tempo.json')
        if os.path.exists(lt):
            r = json.load(open(lt, encoding='utf8'))
            for k in ('textos', 'perfumes', 'broll'):
                for e in r.get(k, []):
                    tempos += [e['ini'] + 0.5]
        tempos = sorted({min(max(0, t), dur - 0.05) for t in tempos})
    folhas = []
    for f0 in range(0, len(tempos), 8):
        bloco = tempos[f0:f0 + 8]
        folha = Image.new('RGB', (270 * len(bloco), 505), (0, 0, 0))
        d = ImageDraw.Draw(folha)
        for i, t in enumerate(bloco):
            q = os.path.join(pasta, '_q.png')
            quadro(video, t, q)
            folha.paste(Image.open(q), (i * 270, 25))
            d.text((i * 270 + 6, 5), f'{t:.2f}s', fill=(255, 230, 0))
        nome = os.path.join(pasta, f'conferir_{len(folhas) + 1:02d}.png')
        folha.save(nome)
        folhas.append(nome)
    os.remove(os.path.join(pasta, '_q.png'))
    print('\n'.join(folhas))
    pausas(video)
    palavras_inteiras(video)


def palavras_inteiras(video):
    """Transcreve o vídeo FINAL e compara com as palavras que deviam estar lá.
    Palavra faltando ou trocada (ex.: "todos" virou "dos") = corte em cima da
    palavra. Tem que dar "todas inteiras"; senão, o trecho volta pro plano."""
    import difflib
    import re
    import unicodedata
    import wave
    import numpy as np
    lt = os.path.join(os.path.dirname(video), 'linha_do_tempo.json')
    if not os.path.exists(lt):
        return
    esperado = json.load(open(lt, encoding='utf8')).get('palavras') or []
    if not esperado:
        return
    from faster_whisper import WhisperModel

    def n(s):
        s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
        return re.sub(r'[^a-z0-9]+', ' ', s).strip()
    wav = os.path.join(os.path.dirname(video), '_conferir.wav')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', video, '-vn', '-ac', '1', '-ar', '16000', wav], check=True)
    with wave.open(wav) as w:
        audio = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    os.remove(wav)
    modelo = None
    for nome in ('small', 'base'):  # PC com pouca memória: tenta o modelo menor
        try:
            modelo = WhisperModel(nome, device='cpu', compute_type='int8')
            break
        except RuntimeError as e:
            print(f'(modelo {nome} sem memória: {e}; tentando menor)')
    if modelo is None:
        print('PALAVRAS: não deu pra conferir (sem memória). Feche programas e rode o conferir.py de novo.')
        return
    segs, _ = modelo.transcribe(audio, language='pt', word_timestamps=True, condition_on_previous_text=False)
    ouvido = [t for s in segs for w in (s.words or []) for t in n(w.word).split()]
    exp = [(t, e['ini']) for e in esperado for t in n(e['p']).split()]
    sm = difflib.SequenceMatcher(a=[t for t, _ in exp], b=ouvido, autojunk=False)
    problemas = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op not in ('delete', 'replace'):
            continue
        falt = [t for t, _ in exp[i1:i2]]
        ouv = ouvido[j1:j2]
        if all(re.fullmatch(r'\d+', x) for x in falt):  # "10" x "dez" não é corte
            continue
        if op == 'replace':
            # grafia diferente do Whisper ("saia" x "saiba", "audeleon") não é corte.
            # Corte é pedaço de palavra: "dos" no lugar de "todos", "perfu" de "perfumes".
            pedaco = any(h != x and 2 <= len(h) < len(x) and (x.endswith(h) or x.startswith(h))
                         for x in falt for h in ouv)
            parecido = difflib.SequenceMatcher(a=''.join(falt), b=''.join(ouv)).ratio() >= 0.5
            if parecido and not pedaco:
                continue
        problemas.append(f'{exp[i1][1]:.2f}s esperado "{" ".join(falt)}" ouvido "{" ".join(ouvido[j1:j2])}"')
    print(f'PALAVRAS (vídeo final x transcrição original, {sm.ratio():.0%} iguais): '
          + ('todas inteiras' if not problemas else 'CONFERIR -> ' + ' | '.join(problemas)))


def pausas(video):
    """Mede o áudio final: lista trechos sem voz >= 0,15 s (respiração/pausa que sobrou)."""
    import numpy as np
    fala = None
    lt = os.path.join(os.path.dirname(video), 'linha_do_tempo.json')
    if os.path.exists(lt):
        fala = json.load(open(lt, encoding='utf8')).get('fala')
    cmd = ['ffmpeg', '-v', 'error', '-i', video] + (['-t', str(fala)] if fala else []) + ['-ac', '1', '-ar', '16000', '-f', 's16le', '-']
    x = np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, np.int16).astype(float)
    j = 160
    n = len(x) // j
    if not n:
        return
    db = 20 * np.log10(np.sqrt((x[:n * j].reshape(n, j) ** 2).mean(1) + 1e-9) / 32768 + 1e-9)
    fraco = db < np.percentile(db, 90) - 24  # abaixo disso é respiro/silêncio (fim de palavra decai até ~-20)
    achou, i = [], 0
    while i < n:
        if fraco[i]:
            k = i
            while k < n and fraco[k]:
                k += 1
            if (k - i) * 0.01 >= 0.15:
                achou.append(f'{i * 0.01:.2f}s ({(k - i) * 0.01:.2f}s)')
            i = k
        else:
            i += 1
    print('PAUSAS que sobraram (>=0,15 s): ' + (', '.join(achou) if achou else 'nenhuma'))


if __name__ == '__main__':
    main()
