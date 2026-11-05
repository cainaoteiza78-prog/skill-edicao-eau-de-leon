"""
Textos na tela, iguais aos criativos da @eau.de.leon (identificados quadro a
quadro em 05/11/2026 — ver treinamento/01):

  legenda   Poppins Bold, branca, sombra preta suave deslocada pra baixo/direita
  impacto   Bebas Neue engrossada (o "negrito" do CapCut), branca, sombra suave,
            1ª linha digitada letra a letra   ex.: "30% DE DESCONTO"
  destaque  Bungee, branca, sombra mais escura, entra com pop   ex.: "QUIZ 100% GRATUITO"
  rotulo    texto nativo do TikTok/Instagram: TikTok Sans SemiBold branca com
            contorno preto fino + emoji colorido   ex.: "POV: Você encontrou...", "Bom 🤗"

A sombra é uma 2ª camada (texto preto, transparente, desfocado e deslocado),
não um contorno — é assim que fica nos reels.
"""
import os
import random
import re

from PIL import Image, ImageDraw, ImageFont

import letreiros

W, H = 1080, 1920
AQUI = os.path.dirname(os.path.abspath(__file__))
FONTES = os.path.normpath(os.path.join(AQUI, '..', 'assets', 'fontes'))

ESTILO_TEXTO = {
    'legenda': {'fonte': 'Poppins', 'arquivo': 'Poppins-Bold.ttf', 'tamanho': 100, 'bold': -1,
                'sombra': (2, 5, 7, 0x48), 'contorno': 3.0, 'contorno_alfa': 0x30},            # dx, dy, desfoque, alfa (00=opaco FF=invisível)
    'impacto': {'fonte': 'Bebas Neue', 'arquivo': 'BebasNeue-Regular.ttf', 'tamanho': 158, 'bold': 0,
                'engrossa': 2.2, 'entrelinha': 0.98, 'digitacao': 0.45, 'sombra': (4, 7, 9, 0x50)},
    'destaque': {'fonte': 'Bungee', 'arquivo': 'Bungee-Regular.ttf', 'tamanho': 239, 'bold': 0,
                 'sub': 0.82, 'entrelinha': 1.06, 'sombra': (5, 8, 5, 0x38)},
    'rotulo': {'arquivo': 'TikTokSans-SemiBold.ttf', 'tamanho': 62, 'contorno': 0.075},
    # palavra-chave do corpo = legenda aumentada (Bebas), ver treinamento/03
    'legenda_grande': {'tamanho': 140, 'linha_de_cima': 0.84, 'sombra': (5, 9, 12, 0x30), 'borda': 4.0, 'borda_alfa': 0x20},
}
LARG_MAX = W * 0.90

# O libass dimensiona pela altura total da fonte (usWinAscent+usWinDescent), não
# pelo "em" — por isso o mesmo s dá tamanhos bem diferentes entre fontes.
# Largura no libass = largura no PIL × fator (medido renderizando de verdade).
_FATOR = {'Poppins-Bold.ttf': 0.559, 'BebasNeue-Regular.ttf': 0.775, 'Bungee-Regular.ttf': 0.388}
# Altura da letra maiúscula desenhada ÷ s (medido). Nos reels as linhas de
# texto grande quase encostam: passo entre linhas = altura da maiúscula × 1,3.
_CAP = {'BebasNeue-Regular.ttf': 0.57, 'Bungee-Regular.ttf': 0.30}
_PASSO = {'BebasNeue-Regular.ttf': 1.30, 'Bungee-Regular.ttf': 1.62}


def caber(texto, arquivo, tam, extra=0.0):
    f = ImageFont.truetype(os.path.join(FONTES, arquivo), tam)
    b = f.getbbox(texto)
    larg = (b[2] - b[0]) * _FATOR.get(arquivo, 0.6) + extra
    return tam if larg <= LARG_MAX else int(tam * LARG_MAX / larg)


def ass_tempo(t):
    t = max(0, t)
    return f'{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}'


def esc(s):
    return s.replace('\\', '\\\\').replace('{', '(').replace('}', ')')


def _par(layer, a, b, estilo, x, y, tam, corpo, sombra, extra_txt='', extra_sombra='', an=5, sombra_corpo=None):
    """Duas linhas ASS: sombra (camada de baixo) + texto branco."""
    dx, dy, blur, alfa = sombra
    s = (f"Dialogue: {layer},{ass_tempo(a)},{ass_tempo(b)},{estilo},,0,0,0,,"
         f"{{\\an{an}\\pos({x + dx},{y + dy})\\fs{tam}\\1c&H000000&\\1a&H{alfa:02X}&\\3c&H000000&\\3a&H{alfa:02X}&"
         f"\\blur{blur}{extra_sombra}}}{sombra_corpo if sombra_corpo is not None else corpo}")
    if estilo == 'Leg' and '\\bord' not in extra_txt:   # legenda: contorno escuro fino
        L = ESTILO_TEXTO['legenda']
        extra_txt = f"\\bord{L['contorno']}\\3c&H000000&\\3a&H{L['contorno_alfa']:02X}&" + extra_txt
    t = (f"Dialogue: {layer + 1},{ass_tempo(a)},{ass_tempo(b)},{estilo},,0,0,0,,"
         f"{{\\an{an}\\pos({x},{y})\\fs{tam}{extra_txt}}}{corpo}")
    return [s, t]


CTAS = []  # CTAs de vidro 3D da edição atual (render.py desenha com cta.py)


def montar_ass(legendas, textos, y_legenda, fim_video=0.0, periodo=1.0):
    L, I, D = ESTILO_TEXTO['legenda'], ESTILO_TEXTO['impacto'], ESTILO_TEXTO['destaque']
    cab = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Leg,{L['fonte']},{L['tamanho']},&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,{L['bold']},0,0,0,100,100,0,0,1,0,0,5,40,40,0,1
Style: Imp,{I['fonte']},{I['tamanho']},&H00FFFFFF,&H00FFFFFF,&H00FFFFFF,&H00000000,0,0,0,0,100,100,1,0,1,{I['engrossa']},0,5,30,30,0,1
Style: Dst,{D['fonte']},{D['tamanho']},&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,30,30,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    n3d = 0
    for l in legendas:
        if not l.get('destaque'):
            tam = caber(l['texto'], L['arquivo'], L['tamanho'])
            ev += _par(1, l['ini'], l['fim'], 'Leg', W // 2, y_legenda, tam, esc(l['texto']), L['sombra'])
            continue
        estilo = l.get('estilo_destaque', '3d')
        if estilo == 'caps':  # só CAIXA ALTA dentro da legenda (como nos anúncios da marca)
            txt = ' '.join(x for x in (l['texto'], l['destaque']) if x)
            tam = caber(txt, L['arquivo'], L['tamanho'])
            ev += _par(1, l['ini'], l['fim'], 'Leg', W // 2, y_legenda, tam, esc(txt), L['sombra'])
            continue
        if estilo == 'botao':
            # CTA: a frase segue normal no peito; o botão de vidro 3D (cta.py) fica abaixo,
            # do instante do "saiba mais" até o fim, pulsando. O render desenha quadro a quadro.
            if l['texto']:
                tam = caber(l['texto'], L['arquivo'], L['tamanho'])
                ev += _par(1, l['ini'], l['fim'], 'Leg', W // 2, y_legenda, tam, esc(l['texto']), L['sombra'])
            CTAS.append({'texto': l['destaque'], 'a': l.get('ini_destaque', l['ini']), 'b': max(fim_video, l['fim']),
                         'cy': min(H - 330, y_legenda + 215), 'periodo': periodo})
            continue
        # palavra-chave: a PRÓPRIA legenda aumentada, como a Eau de Leon faz
        # ("QUE UM DECANT DE 2 ML / RENDE MUITO"): Bebas Neue engrossada, CAIXA ALTA,
        # branca, borda escura fina e sombra maior. A frase sobe pra linha de cima.
        I = ESTILO_TEXTO['impacto']
        G = ESTILO_TEXTO['legenda_grande']
        l1, l2 = l['texto'].upper(), l['destaque'].upper()
        t2 = caber(l2, I['arquivo'], G['tamanho'], extra=24)
        t1 = caber(l1, I['arquivo'], int(G['tamanho'] * G['linha_de_cima']), extra=24) if l1 else 0
        passos = [x * _CAP[I['arquivo']] * _PASSO[I['arquivo']] for x in ([t1] if l1 else []) + [t2]]
        y = y_legenda - sum(passos) / 2
        linhas_ = ([(l1, t1, l['ini'], '')] if l1 else []) + [
            (l2, t2, l.get('ini_destaque', l['ini']), '\\fscx86\\fscy86\\t(0,110,\\fscx104\\fscy104)\\t(110,190,\\fscx100\\fscy100)')]
        for k, (txt, tam, a0, pop) in enumerate(linhas_):
            yc = int(y + passos[k] / 2)
            y += passos[k]
            dx, dy, bl, al = G['sombra']
            base = f'\\an5\\fnBebas Neue\\b0\\fs{tam}\\fsp1'
            ev.append(f"Dialogue: 2,{ass_tempo(a0)},{ass_tempo(l['fim'])},Leg,,0,0,0,,{{{base}\\pos({W // 2 + dx},{yc + dy})"
                      f"\\1c&H000000&\\1a&H{al:02X}&\\3c&H000000&\\3a&H{al:02X}&\\bord{I['engrossa'] + 2}\\blur{bl}{pop}}}{esc(txt)}")
            ev.append(f"Dialogue: 3,{ass_tempo(a0)},{ass_tempo(l['fim'])},Leg,,0,0,0,,{{{base}\\pos({W // 2},{yc})"
                      f"\\1a&HFF&\\3c&H000000&\\3a&H{G['borda_alfa']:02X}&\\bord{I['engrossa'] + G['borda']}{pop}}}{esc(txt)}")
            ev.append(f"Dialogue: 4,{ass_tempo(a0)},{ass_tempo(l['fim'])},Leg,,0,0,0,,{{{base}\\pos({W // 2},{yc})"
                      f"\\1c&HFFFFFF&\\3c&HFFFFFF&\\bord{I['engrossa']}{pop}}}{esc(txt)}")

    rnd = random.Random(7)
    for t in textos:
        a, b = t['ini'], t['fim']
        if t['estilo'] == 'impacto':
            linhas = t['texto'].upper().split('\n')
            tams = [caber(ln, I['arquivo'], I['tamanho'] if n == 0 else int(I['tamanho'] * 0.78), extra=20)
                    for n, ln in enumerate(linhas)]
            passos = [tm * _CAP[I['arquivo']] * _PASSO[I['arquivo']] for tm in tams]
            y = y_legenda - sum(passos) / 2
            for n, (linha, tam) in enumerate(zip(linhas, tams)):
                yc = int(y + passos[n] / 2)
                y += passos[n]
                if n == 0:  # digita letra a letra
                    passo, ordem, t0 = I['digitacao'] * 1000 / max(1, len(linha)), list(range(len(linha))), 0
                else:  # linhas de baixo: letras surgem embaralhadas
                    ordem = list(range(len(linha)))
                    rnd.shuffle(ordem)
                    passo, t0 = 260 / max(1, len(linha)), I['digitacao'] * 800 + (n - 1) * 150
                quando = {i: int(t0 + k * passo) for k, i in enumerate(ordem)}

                def corpo_com(alfa_final):
                    return ''.join(ch if ch == ' ' else
                                   f'{{\\alpha&HFF&\\t({quando[i]},{quando[i] + 40},\\alpha&H{alfa_final:02X}&)}}{esc(ch)}'
                                   for i, ch in enumerate(linha))
                ev += _par(2, a, b, 'Imp', W // 2, yc, tam, corpo_com(0), I['sombra'],
                           extra_txt='\\fad(0,120)', extra_sombra='\\fad(0,120)',
                           sombra_corpo=corpo_com(I['sombra'][3]))
        elif t['estilo'] == 'destaque':
            linhas = t['texto'].upper().split('\n')
            itens = [(ln, caber(ln, D['arquivo'], D['tamanho'])) for ln in linhas]
            if t.get('sub'):
                itens.append((t['sub'].upper(), caber(t['sub'].upper(), D['arquivo'], int(D['tamanho'] * D['sub']))))
            passos = [tm * _CAP[D['arquivo']] * _PASSO[D['arquivo']] for _, tm in itens]
            y = y_legenda - sum(passos) / 2
            pop = '\\fscx60\\fscy60\\t(0,140,\\fscx108\\fscy108)\\t(140,220,\\fscx100\\fscy100)\\fad(0,150)'
            for n, (linha, tam) in enumerate(itens):
                yc = int(y + passos[n] / 2)
                y += passos[n]
                atraso = 0.08 * n
                ev += _par(4, a + atraso, b, 'Dst', W // 2, yc, tam, esc(linha), D['sombra'], extra_txt=pop, extra_sombra=pop)
    return cab + '\n'.join(ev) + '\n'


# ── rótulo (texto nativo TikTok/Instagram com emoji colorido) ───────────────
_EMOJI = re.compile('[\U0001F000-\U0001FAFF☀-➿⬀-⯿️‍\U0001F1E6-\U0001F1FF]+')


def _runs(linha):
    pos, out = 0, []
    for m in _EMOJI.finditer(linha):
        if m.start() > pos:
            out.append(('t', linha[pos:m.start()]))
        out.append(('e', m.group()))
        pos = m.end()
    if pos < len(linha):
        out.append(('t', linha[pos:]))
    return out


def _emoji_img(seq, tam):
    f = ImageFont.truetype(os.path.join(FONTES, 'NotoColorEmoji.ttf'), 109)
    seq = seq.replace('️', '')
    if not seq:
        return None
    im = Image.new('RGBA', (160 * max(1, len(seq)), 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((0, 0), seq, font=f, embedded_color=True)
    bb = im.getbbox()
    if not bb:
        return None
    im = im.crop(bb)
    k = tam * 1.05 / im.height
    return im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.LANCZOS)


def rotulo_png(texto, destino, tam=None):
    """Renderiza o rótulo (pode ter várias linhas e emoji) num PNG transparente. Devolve (w, h)."""
    R = ESTILO_TEXTO['rotulo']
    tam = tam or R['tamanho']
    f = ImageFont.truetype(os.path.join(FONTES, R['arquivo']), tam)
    contorno = max(2, int(tam * R['contorno']))
    linhas_img = []
    for linha in texto.split('\n'):
        partes = []
        for tipo, s in _runs(linha):
            if tipo == 't':
                b = f.getbbox(s, stroke_width=contorno)
                im = Image.new('RGBA', (b[2] - b[0] + 4, int(tam * 1.35) + 2 * contorno), (0, 0, 0, 0))
                ImageDraw.Draw(im).text((-b[0] + 2, contorno), s, font=f, fill='white',
                                        stroke_width=contorno, stroke_fill='black')
                partes.append(im)
            else:
                e = _emoji_img(s, tam)
                if e:
                    partes.append(e)
        if not partes:
            continue
        lw = sum(p.width for p in partes) + 6 * (len(partes) - 1)
        lh = max(p.height for p in partes)
        li = Image.new('RGBA', (lw, lh), (0, 0, 0, 0))
        x = 0
        for p in partes:
            li.alpha_composite(p, (x, (lh - p.height) // 2))
            x += p.width + 6
        linhas_img.append(li)
    if not linhas_img:
        linhas_img = [Image.new('RGBA', (2, 2), (0, 0, 0, 0))]
    larg = max(l.width for l in linhas_img)
    alt = sum(l.height for l in linhas_img) - int(tam * 0.12) * (len(linhas_img) - 1)
    out = Image.new('RGBA', (larg, alt), (0, 0, 0, 0))
    y = 0
    for l in linhas_img:
        out.alpha_composite(l, ((larg - l.width) // 2, y))
        y += l.height - int(tam * 0.12)
    if out.width > W * 0.94:
        k = W * 0.94 / out.width
        out = out.resize((int(out.width * k), int(out.height * k)), Image.LANCZOS)
    out.save(destino)
    return out.size

