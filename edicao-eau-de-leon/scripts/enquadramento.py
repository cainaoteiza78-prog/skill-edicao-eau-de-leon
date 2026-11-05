"""
Onde vai a legenda: abaixo do pescoço, na altura do peito de quem fala.

Acha o rosto (OpenCV, local) num quadro de cada pedaço, leva a caixa do rosto
pro enquadramento final (escala + recorte 9:16 + zoom do pedaço) e põe o
centro da legenda a ~0,6 rosto abaixo do queixo. Usa UMA altura pro vídeo
todo (mediana), como nos reels — a legenda não fica pulando.
"""
import math
import subprocess

import numpy as np

W, H = 1080, 1920
PADRAO = 1080          # sem rosto detectado: altura do peito num plano médio típico
MIN_Y, MAX_Y = 900, 1300


def _quadro(arquivo, t):
    """Um quadro (BGR) já com a rotação do celular aplicada (via ffmpeg)."""
    r = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t:.3f}', '-i', arquivo, '-frames:v', '1',
                        '-f', 'image2pipe', '-vcodec', 'png', '-'], capture_output=True)
    if r.returncode != 0 or not r.stdout:
        return None
    import cv2
    return cv2.imdecode(np.frombuffer(r.stdout, np.uint8), cv2.IMREAD_COLOR)


def rosto(img):
    """(x, y, w, h) do maior rosto, ou None."""
    import cv2
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    esc = 640 / max(g.shape)
    p = cv2.resize(g, (int(g.shape[1] * esc), int(g.shape[0] * esc)))
    cas = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    fs = cas.detectMultiScale(p, scaleFactor=1.1, minNeighbors=6, minSize=(40, 40))
    if len(fs) == 0:
        return None
    x, y, w, h = max(fs, key=lambda f: f[2] * f[3])
    return x / esc, y / esc, w / esc, h / esc


def para_saida(caixa, sw, sh, zoom, foco_x, foco_y):
    """Caixa do rosto na take → caixa no quadro 1080x1920 do pedaço."""
    par = lambda v: int(math.ceil(v / 2) * 2)
    tw, th = par(W * zoom), par(H * zoom)
    k = max(tw / sw, th / sh)          # scale ... force_original_aspect_ratio=increase
    nw, nh = sw * k, sh * k
    ox, oy = (nw - W) * foco_x, (nh - H) * foco_y
    x, y, w, h = caixa
    return x * k - ox, y * k - oy, w * k, h * k


def altura_legenda(segs, takes):
    """Centro Y da legenda pro vídeo todo + caixas de rosto achadas (pra conferência)."""
    ys, achados = [], []
    # a legenda é fixa: mede nos planos normais (zoom 1,0); os com zoom puxam pra baixo
    base = [s for s in segs if s['zoom'] <= 1.0] or segs
    for s in base[:: max(1, len(base) // 8)]:  # até ~8 amostras
        arq = takes[s['take'] - 1]['arquivo']
        img = _quadro(arq, (s['a'] + s['b']) / 2)
        if img is None:
            continue
        c = rosto(img)
        if not c:
            continue
        sh, sw = img.shape[:2]
        x, y, w, h = para_saida(c, sw, sh, s['zoom'], s['foco_x'], s['foco_y'])
        queixo = y + h
        ys.append(queixo + 0.6 * h)
        achados.append((round(x), round(y), round(w), round(h)))
    if not ys:
        return PADRAO, achados
    return int(min(MAX_Y, max(MIN_Y, float(np.median(ys))))), achados
