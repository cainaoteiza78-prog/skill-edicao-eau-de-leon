"""
Revisão automática do vídeo editado (roda junto com o conferir.py). Mede, no
vídeo FINAL, o que o olho às vezes não pega nas folhas de quadros:

  1. LEGENDAS SOBREPOSTAS: dois textos de legenda/destaque na tela ao mesmo
     tempo (lido do legenda.ass: só conta texto, não sombra/borda da mesma frase).
  2. CENTRALIZAÇÃO: o rosto da pessoa a cada 0,25 s; acusa quando o centro do
     rosto sai mais de 5% do meio da tela.
  3. POSIÇÃO DA LEGENDA: onde a legenda ficou em relação ao queixo (tem que
     estar no PEITO: pelo menos ~0,8 rosto abaixo do queixo).

Uso:  python revisar.py <trabalho>/editado.mp4
Saída: uma linha por item, "OK" ou "PROBLEMA -> ...". Não entregue com PROBLEMA.
"""
import sys as _sys
_sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import json
import os
import re
import subprocess
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from enquadramento import rosto  # noqa: E402

W, H = 1080, 1920


def _t(s):
    h, m, x = s.split(':')
    return int(h) * 3600 + int(m) * 60 + float(x)


def legendas_sobrepostas(ass):
    """Eventos de TEXTO (camada da frente de cada legenda) que se cruzam no tempo."""
    evs = []
    for l in open(ass, encoding='utf8'):
        if not l.startswith('Dialogue:'):
            continue
        partes = l.split(',', 9)
        camada, a, b, txt = int(partes[0].split()[1]), _t(partes[1]), _t(partes[2]), partes[9]
        tags = ''.join(re.findall(r'\{([^}]*)\}', txt))
        corpo = re.sub(r'\{[^}]*\}', '', txt).strip()
        if not corpo or '\\p1' in tags:
            continue
        if '\\1c&H000000&' in tags or '\\1a&HFF&' in tags.split('\\t')[0] and '\\3c&H000000&' in tags:
            continue   # sombra / borda (camada de trás da mesma frase)
        if '\\blur' in tags and '\\1c&H000000&' in tags:
            continue
        pos = re.search(r'\\pos\((\d+),(\d+)\)', tags)
        y = int(pos.group(2)) if pos else 0
        evs.append((a, b, corpo, y, camada))
    # mesma frase em camadas diferentes (borda + texto) não conta: agrupa por (a,b,corpo)
    unicos = {}
    for a, b, c, y, cam in evs:
        unicos.setdefault((round(a, 2), round(b, 2), c), (a, b, c, y))
    evs = sorted(unicos.values())
    probs = []
    for i in range(len(evs)):
        for j in range(i + 1, len(evs)):
            a1, b1, c1, y1 = evs[i]
            a2, b2, c2, y2 = evs[j]
            if a2 >= b1:
                break
            sob = min(b1, b2) - max(a1, a2)
            mesmo_elemento = abs(b1 - b2) < 0.01 and abs(a1 - a2) < 0.4   # linhas de um mesmo título
            if sob > 0.02 and abs(y1 - y2) < 140 and not mesmo_elemento:
                probs.append(f'{max(a1, a2):.2f}s "{c1}" x "{c2}" ({sob:.2f}s)')
    return probs


def rostos(video, passo=0.5):
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', video],
                               capture_output=True, text=True).stdout)
    import cv2
    out = []
    t = 0.2
    while t < dur - 0.1:
        r = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t:.2f}', '-i', video, '-frames:v', '1',
                            '-f', 'image2pipe', '-vcodec', 'png', '-'], capture_output=True)
        img = cv2.imdecode(np.frombuffer(r.stdout, np.uint8), cv2.IMREAD_COLOR) if r.stdout else None
        c = rosto(img) if img is not None else None
        out.append((t, c))
        t += passo
    return out


def main():
    video = os.path.abspath(sys.argv[1])
    pasta = os.path.dirname(video)
    ass = os.path.join(pasta, '_render', 'legenda.ass')
    lt = json.load(open(os.path.join(pasta, 'linha_do_tempo.json'), encoding='utf8'))
    s = legendas_sobrepostas(ass)
    print('SOBREPOSIÇÃO de legendas: ' + ('OK' if not s else 'PROBLEMA -> ' + ' | '.join(s[:8])))
    rs = rostos(video)
    fora, queixos = [], []
    for t, c in rs:
        if not c:
            continue
        x, y, w, h = c
        cx = (x + w / 2) / W
        if abs(cx - 0.5) > 0.05:
            fora.append(f'{t:.2f}s ({cx:.0%})')
        queixos.append((y + h, h))
    print(f'CENTRALIZAÇÃO ({len([1 for _, c in rs if c])} quadros com rosto): '
          + ('OK' if not fora else f'PROBLEMA -> rosto fora do centro em {len(fora)}: ' + ', '.join(fora[:10])))
    if queixos:
        qy = float(np.median([q for q, _ in queixos]))
        fh = float(np.median([h for _, h in queixos]))
        ly = lt.get('legenda_y', 0)
        dist = (ly - qy) / fh
        print(f'POSIÇÃO da legenda: y={ly}, {dist:.2f} rosto abaixo do queixo -> '
              + ('OK (peito)' if dist >= 0.8 else 'PROBLEMA -> alta demais (pescoço)'))


if __name__ == '__main__':
    main()
