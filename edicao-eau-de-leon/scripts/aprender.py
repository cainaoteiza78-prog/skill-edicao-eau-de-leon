"""
Base de conhecimento LOCAL da skill: o que o usuário (editor) pediu pra mudar vira regra
permanente, pra a skill não repetir o erro nas próximas edições.

  python aprender.py listar                       # mostra todas as lições (ler ANTES de editar)
  python aprender.py adicionar --area cta \\
      --pedido "o saiba mais ficou grande demais" \\
      --regra "placa do SAIBA MAIS sempre do tamanho da legenda comum" \\
      --como "conferir no quadro final; se maior, reduzir em cta.py" \\
      [--video "Light Blue 06/11"] [--mudou "scripts/cta.py: tam = legenda"]
  python aprender.py exportar                     # imprime a base inteira (pra mandar pro dono da skill)

A base fica em <skill>/aprendizados/aprendizados.md. Ela é da MÁQUINA (não vem do
GitHub) e os instaladores a preservam nas atualizações. Lição repetida (mesma área e
regra parecida) não duplica: o contador "pedido N vezes" sobe — sinal de que a skill
está insistindo no erro e a regra precisa ser seguida com mais rigor.
"""
import argparse
import datetime
import difflib
import io
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
PASTA = os.path.normpath(os.path.join(AQUI, '..', 'aprendizados'))
ARQ = os.path.join(PASTA, 'aprendizados.md')
AREAS = ['cortes', 'bastidor', 'legenda', 'destaques', 'textos', 'cta', 'perfumes', 'broll',
         'enquadramento', 'audio', 'musica', 'cores', 'ritmo', 'entrega', 'outro']
CABECALHO = """# Aprendizados desta máquina (base de conhecimento da skill)

Cada lição abaixo veio de um pedido de alteração do usuário. **Elas valem mais que o
treinamento**: se uma lição contradiz um arquivo de `treinamento/`, siga a lição (é o
pedido mais recente de quem usa a skill). Leia tudo antes de cada edição.

"""
RE_LICAO = re.compile(r'^## (\d+)\. \[(\w+)\] (.+)$', re.M)


def ler():
    if not os.path.exists(ARQ):
        return CABECALHO
    return io.open(ARQ, encoding='utf-8').read()


def gravar(txt):
    os.makedirs(PASTA, exist_ok=True)
    io.open(ARQ, 'w', encoding='utf-8').write(txt)


def norm(s):
    return re.sub(r'\s+', ' ', s.lower()).strip()


def adicionar(a):
    if a.area not in AREAS:
        sys.exit(f'área inválida: {a.area}. Use uma de: {", ".join(AREAS)}')
    txt = ler()
    hoje = datetime.date.today().strftime('%d/%m/%Y')
    # já existe lição parecida na mesma área? sobe o contador em vez de duplicar
    for m in RE_LICAO.finditer(txt):
        num, area, regra = m.group(1), m.group(2), m.group(3)
        if area == a.area and difflib.SequenceMatcher(None, norm(regra), norm(a.regra)).ratio() >= 0.72:
            ini = m.end()
            prox = RE_LICAO.search(txt, ini)
            bloco = txt[ini:prox.start() if prox else len(txt)]
            c = re.search(r'pedido (\d+) vez', bloco, re.I)
            n = int(c.group(1)) + 1 if c else 2
            novo = re.sub(r'- \*\*Pedido \d+ vez(es)?\*\*[^\n]*', '', bloco).rstrip('\n')
            novo += f'\n- **Pedido {n} vezes** (último em {hoje}: "{a.pedido}"). ATENÇÃO: o erro voltou — siga esta regra à risca.\n\n'
            txt = txt[:ini] + novo + (txt[prox.start():] if prox else '')
            gravar(txt)
            print(f'Lição {num} já existia — contador subiu pra {n}. Base: {ARQ}')
            return
    nums = [int(x) for x in re.findall(r'^## (\d+)\.', txt, re.M)]
    n = max(nums, default=0) + 1
    linhas = [f'## {n}. [{a.area}] {a.regra.strip()}',
              f'- **Data:** {hoje}' + (f' — vídeo: {a.video}' if a.video else ''),
              f'- **O que o usuário pediu:** "{a.pedido.strip()}"']
    if a.como:
        linhas.append(f'- **Como aplicar:** {a.como.strip()}')
    if a.mudou:
        linhas.append(f'- **O que foi mudado na skill:** {a.mudou.strip()}')
    if not txt.endswith('\n\n'):
        txt = txt.rstrip('\n') + '\n\n'
    gravar(txt + '\n'.join(linhas) + '\n\n')
    print(f'Lição {n} gravada em {ARQ}')


def listar(_a=None):
    txt = ler()
    if not RE_LICAO.search(txt):
        print('Nenhuma lição ainda (base vazia).')
        return
    print(txt)


def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    ap = argparse.ArgumentParser(description='Base de conhecimento local da skill de edição.')
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('adicionar')
    s.add_argument('--area', required=True, help=' | '.join(AREAS))
    s.add_argument('--pedido', required=True, help='o que o usuário pediu, com as palavras dele')
    s.add_argument('--regra', required=True, help='a regra GERAL que vale para todo vídeo daqui pra frente')
    s.add_argument('--como', help='como aplicar/conferir nas próximas edições')
    s.add_argument('--video', help='qual vídeo originou a lição')
    s.add_argument('--mudou', help='arquivo/parâmetro alterado na skill, se houve')
    sub.add_parser('listar')
    sub.add_parser('exportar')
    a = ap.parse_args()
    if a.cmd == 'adicionar':
        adicionar(a)
    else:
        listar()


if __name__ == '__main__':
    main()
