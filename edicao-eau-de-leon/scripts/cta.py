"""
CTA final em glassmorphism 3D ("SAIBA MAIS", "LINK NA BIO"...), desenhado
quadro a quadro (PIL), porque textura e brilho não existem em legenda ASS.

A peça é uma placa de VIDRO flutuando em 3D:
  - fundo: o vídeo atrás fica desfocado de verdade (render.py recorta, desfoca
    e aplica a máscara que este módulo gera pra cada quadro);
  - placa: vidro TRANSPARENTE e borrado, quase sem cor (só um véu leve da
    cor da marca), do tamanho da legenda comum; borda de luz no topo, reflexo
    diagonal, espessura (lateral 3D) e sombra difusa no "chão";
  - perspectiva: a placa está levemente inclinada (topo mais estreito), como
    um cartão flutuando na frente da pessoa;
  - texto: também de vidro — degradê da mesma cor (claro em cima, mais
    saturado embaixo), textura granulada, GLOW da própria cor, fio de luz em
    cima das letras e sombra interna;
  - movimento: entra saltando (0,35 s), depois pulsa devagar no ritmo da fala
    e flutua levemente pra cima e pra baixo, até o fim do vídeo.

Paletas (vidro e texto da mesma família, ver treinamento/03):
  coral (padrão)  #FF9A86 → #E8604E   (do rosa do logo, "TOP Mais Vendidos")
  azul            #A9D3F0 → #4E8FBF   (do azul do logo, "NO BOLSO")
"""
import math
import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
FONTES = os.path.normpath(os.path.join(AQUI, '..', 'assets', 'fontes'))
FPS = 30

# SEMPRE as cores da Eau de Leon (logo): rosa #F2A595 ou azul #6BA9CF, com leve
# fade lateral (degradê da esquerda pra direita). Vidro = mesma cor, mais escura e suave.
PALETAS = {
    'rosa': {'claro': (255, 228, 220), 'meio': (242, 165, 149), 'escuro': (238, 138, 120), 'vidro': (140, 70, 72)},
    'azul': {'claro': (228, 244, 255), 'meio': (120, 186, 230), 'escuro': (118, 180, 224), 'vidro': (30, 66, 98)},
}


def _degrade(w, h, c0, c1):
    t = np.linspace(0, 1, h)[:, None, None]
    a = np.array(c0, float)[None, None, :]
    b = np.array(c1, float)[None, None, :]
    return np.repeat((a + (b - a) * t), w, axis=1)


def _ruido(w, h, forca, semente=3):
    rs = np.random.RandomState(semente)
    n = rs.normal(0, 1, (h, w))
    n = np.asarray(Image.fromarray(((n * 40) + 128).clip(0, 255).astype('uint8')).filter(ImageFilter.GaussianBlur(0.6)), float)
    return (n - 128) / 40 * forca


def _arredondado(w, h, r, fill=255):
    m = Image.new('L', (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), radius=r, fill=fill)
    return m


def _texto_vidro(txt, tam, pal):
    """Texto com degradê + grão + fio de luz + glow. Devolve RGBA com margem pro glow."""
    f = ImageFont.truetype(os.path.join(FONTES, 'Poppins-Bold.ttf'), tam)
    esp = int(tam * 0.04)
    larg = sum(f.getbbox(ch)[2] for ch in txt) + esp * (len(txt) - 1)
    asc, desc = f.getmetrics()
    m = int(tam * 0.5)
    W_, H_ = int(larg + 2 * m), int(asc + desc + 2 * m)
    mask = Image.new('L', (W_, H_), 0)
    d = ImageDraw.Draw(mask)
    x = m
    for ch in txt:
        d.text((x, m), ch, font=f, fill=255)
        x += f.getbbox(ch)[2] + esp
    bb = mask.getbbox()
    # preenchimento: degradê vertical dentro das letras + grão
    top, bot = bb[1], bb[3]
    grad = np.zeros((H_, W_, 3))
    esq, dir_ = bb[0], bb[2]
    fx = np.clip((np.arange(W_) - esq) / max(1, dir_ - esq), 0, 1)[None, :, None]
    a0, a1 = np.array(pal['claro'], float), np.array(pal['escuro'], float)
    lateral = a0 + (a1 - a0) * fx                                   # fade lateral
    fy = np.clip((np.arange(H_) - top) / max(1, bot - top), 0, 1)[:, None, None]
    grad = lateral * (1.04 - 0.10 * fy)                             # um tico mais claro em cima
    grad += _ruido(W_, H_, 14)[:, :, None]
    face = Image.fromarray(grad.clip(0, 255).astype('uint8')).convert('RGBA')
    face.putalpha(mask)
    # fio de luz em cima de cada letra (borda superior clara)
    a = np.asarray(mask, float)
    cima = (a - np.roll(a, 3, axis=0)).clip(0, 255)
    luz = Image.new('RGBA', (W_, H_), (255, 255, 255, 0))
    luz.putalpha(Image.fromarray((cima * 0.55).astype('uint8')).filter(ImageFilter.GaussianBlur(1)))
    # sombra interna embaixo
    baixo = (a - np.roll(a, -4, axis=0)).clip(0, 255)
    sint = Image.new('RGBA', (W_, H_), (90, 30, 24, 0) if pal is PALETAS['rosa'] else (10, 30, 60, 0))
    sint.putalpha(Image.fromarray((baixo * 0.35).astype('uint8')).filter(ImageFilter.GaussianBlur(1.5)))
    # glow da própria cor
    glow = Image.new('RGBA', (W_, H_), pal['meio'] + (0,))
    glow.putalpha(mask.filter(ImageFilter.GaussianBlur(tam * 0.20)).point(lambda v: min(255, int(v * 1.7))))
    glow2 = Image.new('RGBA', (W_, H_), pal['claro'] + (0,))
    glow2.putalpha(mask.filter(ImageFilter.GaussianBlur(tam * 0.05)).point(lambda v: int(v * 0.5)))
    # sombra que "descola" o texto da placa (3D)
    som = Image.new('RGBA', (W_, H_), (0, 0, 0, 0))
    som.putalpha(mask.filter(ImageFilter.GaussianBlur(5)).point(lambda v: int(v * 0.45)))
    out = Image.new('RGBA', (W_, H_), (0, 0, 0, 0))
    out.alpha_composite(glow)
    out.alpha_composite(som, (3, 7))
    out.alpha_composite(glow2)
    out.alpha_composite(face)
    out.alpha_composite(sint)
    out.alpha_composite(luz)
    return out


def _perspectiva(im, inclina=0.018, giro=0.0):
    """Inclina a placa: topo um pouco mais estreito (vista de baixo), leve giro lateral."""
    w, h = im.size
    dx = w * inclina
    dy = h * giro
    # destino (quadrilátero) → coeficientes da transformação inversa
    src = [(0, 0), (w, 0), (w, h), (0, h)]
    dst = [(dx, dy), (w - dx, -dy), (w, h), (0, h)]
    mat = []
    for (x, y), (u, v) in zip(dst, src):
        mat.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
        mat.append([0, 0, 0, x, y, 1, -v * x, -v * y])
    A = np.array(mat, float)
    B = np.array([c for p in src for c in p], float)
    coef = np.linalg.solve(A, B)
    return im.transform((w, h), Image.PERSPECTIVE, coef, Image.BICUBIC)


def tam_por_cap(cap_px):
    """Tamanho PIL da Poppins Bold cuja maiúscula tem `cap_px` de altura (= a da legenda comum)."""
    f = ImageFont.truetype(os.path.join(FONTES, 'Poppins-Bold.ttf'), 100)
    b = f.getbbox('H')
    return max(30, int(round(cap_px / ((b[3] - b[1]) / 100))))


def montar(txt, larg_max=640, paleta='rosa', tam=None):
    """Peça base (RGBA) + máscara da face de vidro (L).

    TAMANHO (06/11, dono): o elemento inteiro é do tamanho da legenda comum. As letras
    têm a mesma altura da legenda (`tam`, vindo do render) e a placa só abraça o texto.
    VIDRO (06/11, dono): transparente e borrado; quase sem cor — só um véu leve da cor
    da marca pra dar a sensação de vidro. A cor forte fica só nas letras.
    """
    pal = PALETAS[paleta]
    tam = tam or 128
    tx = _texto_vidro(txt.upper(), tam, pal)
    while tx.width - tam > larg_max - 80 and tam > 40:
        tam -= 4
        tx = _texto_vidro(txt.upper(), tam, pal)
    k = tam / 128                  # tudo proporcional ao tamanho da letra
    tb = tx.getbbox()
    tw, th = tb[2] - tb[0], tb[3] - tb[1]
    bw, bh = int(tw + 110 * k), int(th + 84 * k)
    r = int(bh * 0.32)
    esp = max(6, int(22 * k))      # espessura (lateral 3D)
    marg = max(40, int(100 * k))   # espaço pra sombra/glow
    W_, H_ = bw + 2 * marg, bh + esp + 2 * marg
    peca = Image.new('RGBA', (W_, H_), (0, 0, 0, 0))
    x0, y0 = marg, marg
    # sombra no chão (flutuando) — mais leve: a placa é pequena e transparente
    sh = Image.new('RGBA', (W_, H_), (0, 0, 0, 0))
    sh.paste((0, 0, 0, 150), (x0 + int(6 * k), y0 + esp + int(44 * k)), _arredondado(max(4, bw - int(12 * k)), max(4, bh - 4), r))
    peca.alpha_composite(sh.filter(ImageFilter.GaussianBlur(max(8, 30 * k))))
    sc = Image.new('RGBA', (W_, H_), (0, 0, 0, 0))
    sc.paste((0, 0, 0, 110), (x0 + 3, y0 + esp + int(6 * k)), _arredondado(bw - 6, bh, r))
    peca.alpha_composite(sc.filter(ImageFilter.GaussianBlur(max(4, 9 * k))))
    fm = _arredondado(bw, bh, r)
    fa = np.asarray(fm, float) / 255
    # espessura: só a aresta clara que sobra embaixo da face, quase branca e translúcida
    aresta = np.zeros((bh + esp, bw))
    for j in range(1, esp + 1):
        aresta[j:j + bh] = np.maximum(aresta[j:j + bh], fa)
    aresta[:bh] = aresta[:bh] * (1 - fa)
    claro = tuple(min(255, int(v * 0.15 + 255 * 0.85)) for v in pal['meio'])
    edge = np.zeros((bh + esp, bw, 4))
    edge[:, :, :3] = np.array(claro, float)
    edge[:, :, 3] = aresta * np.linspace(1.0, 0.55, bh + esp)[:, None] * 90
    peca.alpha_composite(Image.fromarray(edge.clip(0, 255).astype('uint8'), 'RGBA'), (x0, y0))
    # face: vidro TRANSPARENTE — branco gelo com um véu bem leve da cor da marca
    # (fade lateral). O fundo borrado de verdade (render.py) é o que se vê através.
    face = np.zeros((bh, bw, 4))
    vx = np.linspace(1.0, 0.0, bw)[None, :, None]
    tinta = np.array(pal['meio'], float) * 0.30 + 255 * 0.70        # pouca cor
    branco = np.array((255, 255, 255), float)
    face[:, :, :3] = branco * vx + tinta * (1 - vx)
    face[:, :, 3] = (np.linspace(0.16, 0.10, bh)[:, None] * 255) * fa
    face[:, :, :3] += _ruido(bw, bh, 5, 7)[:, :, None]              # grão fosco
    peca.alpha_composite(Image.fromarray(face.clip(0, 255).astype('uint8'), 'RGBA'), (x0, y0))
    # reflexo diagonal (luz batendo no vidro)
    refl = Image.new('L', (bw, bh), 0)
    ImageDraw.Draw(refl).polygon([(bw * 0.08, 0), (bw * 0.34, 0), (bw * 0.18, bh), (-bw * 0.08, bh)], fill=45)
    refl = Image.fromarray((np.asarray(refl.filter(ImageFilter.GaussianBlur(max(4, 18 * k))), float) * np.asarray(fm) / 255).astype('uint8'))
    rl = Image.new('RGBA', (bw, bh), (255, 255, 255, 0))
    rl.putalpha(refl)
    peca.alpha_composite(rl, (x0, y0))
    # brilho no topo
    topo = Image.new('L', (bw, bh), 0)
    ImageDraw.Draw(topo).rounded_rectangle((4, 3, bw - 5, int(bh * 0.42)), radius=max(4, r - 4), fill=34)
    topo = topo.filter(ImageFilter.GaussianBlur(max(3, 8 * k)))
    tl = Image.new('RGBA', (bw, bh), (255, 255, 255, 0))
    tl.putalpha(Image.fromarray((np.asarray(topo, float) * np.asarray(fm) / 255).astype('uint8')))
    peca.alpha_composite(tl, (x0, y0))
    # borda de luz branca: mais forte em cima, some embaixo
    bd = Image.new('L', (bw, bh), 0)
    ImageDraw.Draw(bd).rounded_rectangle((1, 1, bw - 2, bh - 2), radius=r, outline=255, width=max(2, int(3 * k)))
    grad_b = np.linspace(0.75, 0.20, bh)[:, None]
    bl = Image.new('RGBA', (bw, bh), (255, 255, 255, 0))
    bl.putalpha(Image.fromarray((np.asarray(bd, float) * grad_b).astype('uint8')))
    peca.alpha_composite(bl, (x0, y0))
    peca.alpha_composite(tx, (int(x0 + bw / 2 - (tb[0] + tw / 2)), int(y0 + bh / 2 - (tb[1] + th / 2)) - 1))
    mask = Image.new('L', (W_, H_), 0)
    mask.paste(fm, (x0, y0))
    peca, mask = _perspectiva(peca), _perspectiva(mask)
    return peca, mask.filter(ImageFilter.GaussianBlur(2))


def quadros(txt, dur, periodo, pasta, paleta='rosa', larg_max=640, tam=None):
    """Grava cta_####.png (peça) e ctam_####.png (máscara) pra cada quadro de `dur` s.
    Devolve (largura, altura) do quadro — todos do mesmo tamanho (escala máx.)."""
    peca, mask = montar(txt, larg_max, paleta, tam)
    esc_max = 1.10
    W_, H_ = int(peca.width * esc_max) // 2 * 2, int(peca.height * esc_max) // 2 * 2
    n = max(1, int(round(dur * FPS)))
    for i in range(n):
        t = i / FPS
        if t < 0.35:                                   # entrada: salta da tela
            p = t / 0.35
            esc = 0.55 + 0.53 * (1 - (1 - p) ** 3) - 0.08 * math.sin(p * math.pi)
            op = min(1, p * 2.2)
        else:                                          # pulso lento no ritmo da fala
            fase = ((t - 0.35) % periodo) / periodo
            esc = 1.0 + 0.05 * math.sin(fase * math.pi) ** 2
            op = 1
        flutua = 6 * math.sin(2 * math.pi * t / (periodo * 2.6))
        w, h = max(2, int(peca.width * esc)), max(2, int(peca.height * esc))
        quadro = Image.new('RGBA', (W_, H_), (0, 0, 0, 0))
        qm = Image.new('L', (W_, H_), 0)
        px, py = (W_ - w) // 2, int((H_ - h) // 2 + flutua)
        pz = peca.resize((w, h), Image.BILINEAR)
        if op < 1:
            pz.putalpha(pz.getchannel('A').point(lambda v: int(v * op)))
        quadro.alpha_composite(pz, (px, py))
        mz = mask.resize((w, h), Image.BILINEAR)
        if op < 1:
            mz = mz.point(lambda v: int(v * op))
        qm.paste(mz, (px, py))
        quadro.save(os.path.join(pasta, f'cta_{i:04d}.png'), compress_level=1)
        qm.save(os.path.join(pasta, f'ctam_{i:04d}.png'), compress_level=1)
    return W_, H_
