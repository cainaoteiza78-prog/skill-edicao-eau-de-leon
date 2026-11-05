"""
Destaques em GLASSMORPHISM (vidro fosco), com aparência realista e premium.

Cada destaque é um painel de vidro:
  1. o VÍDEO atrás do painel fica desfocado de verdade (o render recorta,
     desfoca e devolve aquele pedaço; ver CAIXAS e render.py);
  2. uma película translúcida por cima (branca ou levemente colorida);
  3. borda fina de luz (1,5 px, branco 45%) e um reflexo suave no topo;
  4. sombra larga e difusa embaixo (o painel "flutua" sobre o vídeo);
  5. texto limpo: Poppins Bold em CAIXA ALTA, espaçado, com sombra sutil.

  vidro  palavra-chave da oferta ("10% DE DESCONTO", "TODOS OS PERFUMES").
         Película em rodízio: clara, azul da marca, rosa da marca.
  botao  "SAIBA MAIS" e outros CTAs: pílula de vidro ESCURO (contraste em
         qualquer fundo), maior que os outros textos, com halo leve, e que
         pulsa devagar no ritmo da fala até o fim do vídeo.
  caps   sem painel: CAIXA ALTA dentro da legenda (nome de perfume).

Entradas discretas (sobe 24 px + aparece em 0,22 s). Nada de giro, quique ou
cor saturada: isso é o que deixava o visual infantil.
"""
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
AQUI = os.path.dirname(os.path.abspath(__file__))
FONTES = os.path.normpath(os.path.join(AQUI, '..', 'assets', 'fontes'))

MARCA = {'rosa': '#F2A595', 'azul': '#6BA9CF', 'escuro': '#151A22', 'branco': '#FFFFFF'}
# película do vidro (cor, opacidade 0..1) em rodízio
PELICULAS = [('#FFFFFF', 0.16), ('#6BA9CF', 0.22), ('#F2A595', 0.22)]
CTA_BOTAO = ['saiba mais', 'clique aqui', 'clica aqui', 'link na bio', 'compre agora', 'garanta o seu', 'garante o seu']

ARQ = 'Poppins-Bold.ttf'
FATOR = 0.559      # largura libass / largura PIL (Poppins, medido)
CAP = 0.40         # altura da maiúscula / \fs no libass (Poppins)

# Painéis da edição atual: o render usa pra desfocar o vídeo atrás de cada um.
CAIXAS = []


def cor(hexa):
    r, g, b = (int(hexa[k:k + 2], 16) for k in (1, 3, 5))
    return f'&H{b:02X}{g:02X}{r:02X}&'


def alfa(opac):
    """opacidade 0..1 → alfa ASS (00 = opaco, FF = invisível)."""
    return f'&H{max(0, min(255, round(255 * (1 - opac)))):02X}&'


def tempo(t):
    t = max(0, t)
    return f'{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}'


def esc(s):
    return s.replace('\\', '\\\\').replace('{', '(').replace('}', ')')


def retangulo(w, h, r):
    r = min(r, h / 2, w / 2)
    k = r * 0.45
    return (f'm {r:.1f} 0 l {w - r:.1f} 0 b {w - k:.1f} 0 {w} {k:.1f} {w} {r:.1f} l {w} {h - r:.1f} '
            f'b {w} {h - k:.1f} {w - k:.1f} {h} {w - r:.1f} {h} l {r:.1f} {h} b {k:.1f} {h} 0 {h - k:.1f} 0 {h - r:.1f} '
            f'l 0 {r:.1f} b 0 {k:.1f} {k:.1f} 0 {r:.1f} 0')


def largura(texto, tam, esp=0):
    f = ImageFont.truetype(os.path.join(FONTES, ARQ), tam)
    b = f.getbbox(texto)
    return (b[2] - b[0]) * FATOR + esp * max(0, len(texto) - 1)


def _linha(camada, a, b, tags, corpo):
    return f'Dialogue: {camada},{tempo(a)},{tempo(b)},Leg,,0,0,0,,{{{tags}}}{corpo}'


def _medidas(txt, alvo_cap, lim, padx, pady, esp):
    tam = int(alvo_cap / CAP)
    larg = largura(txt, tam, esp)
    if larg > lim - 2 * padx:
        f = (lim - 2 * padx) / larg
        tam, larg = int(tam * f), larg * f
    cap = tam * CAP
    return tam, cap, int(larg + 2 * padx), int(cap + 2 * pady)


def _painel(ev, a, b, cx, cy, bw, bh, raio, pelicula, opac, anim, borda_opac=0.45, sombra_opac=0.35):
    """Camadas ASS do vidro (o desfoque do fundo é feito pelo render via CAIXAS)."""
    x0, y0 = cx - bw / 2, cy - bh / 2
    forma = retangulo(bw, bh, raio)
    # sombra difusa (flutuando)
    ev.append(_linha(30, a, b, f'\\an7\\pos({x0:.0f},{y0 + 18:.0f})\\1c&H000000&\\1a{alfa(sombra_opac)}\\bord0\\shad0\\blur22{anim}\\p1', forma))
    # película
    ev.append(_linha(31, a, b, f'\\an7\\pos({x0:.0f},{y0:.0f})\\1c{cor(pelicula)}\\1a{alfa(opac)}\\bord0\\shad0{anim}\\p1', forma))
    # reflexo no topo (luz vindo de cima)
    rh = bh * 0.46
    ev.append(_linha(32, a, b, f'\\an7\\pos({x0 + 4:.0f},{y0 + 3:.0f})\\1c&HFFFFFF&\\1a{alfa(0.10)}\\bord0\\shad0\\blur6{anim}\\p1',
                     retangulo(bw - 8, rh, max(4, raio - 3))))
    # borda de luz
    ev.append(_linha(33, a, b, f'\\an7\\pos({x0:.0f},{y0:.0f})\\1a&HFF&\\3c&HFFFFFF&\\3a{alfa(borda_opac)}\\bord1.6\\shad0{anim}\\p1', forma))


def _texto(ev, a, b, cx, cy, tam, txt, esp, anim, cor_txt='#FFFFFF'):
    base = f'\\an5\\fnPoppins\\b1\\fs{tam}\\fsp{esp}\\bord0'
    ev.append(_linha(34, a, b, f'{base}\\pos({cx + 2},{cy + 4})\\1c&H000000&\\1a{alfa(0.35)}\\blur5{anim}', esc(txt)))
    ev.append(_linha(35, a, b, f'{base}\\pos({cx},{cy})\\1c{cor(cor_txt)}{anim}', esc(txt)))


ENTRADA = '\\alpha&HFF&\\t(0,220,\\alpha&H00&)'   # só aparece; o movimento vai no \move


def texto_3d(texto, a, b, cx, cy, variacao=0):
    """Palavra-chave num painel de vidro fosco. (Mantém o nome por compatibilidade.)"""
    txt = texto.upper()
    esp = 3
    tam, cap, bw, bh = _medidas(txt, 58, W * 0.86, 52, 34, esp)
    pel, opac = PELICULAS[variacao % len(PELICULAS)]
    ev = []
    anim_in = f'\\fad(220,160)'
    # sobe 24 px ao entrar: usa \move nas camadas de texto; o painel aparece no lugar
    _painel(ev, a, b, cx, cy, bw, bh, 30, pel, opac, anim_in)
    base = f'\\an5\\fnPoppins\\b1\\fs{tam}\\fsp{esp}\\bord0'
    ev.append(_linha(34, a, b, f'{base}\\move({cx + 2},{cy + 28},{cx + 2},{cy + 4},0,220)\\1c&H000000&\\1a{alfa(0.35)}\\blur5{anim_in}', esc(txt)))
    ev.append(_linha(35, a, b, f'{base}\\move({cx},{cy + 24},{cx},{cy},0,220)\\1c&HFFFFFF&{anim_in}', esc(txt)))
    CAIXAS.append({'x': int(cx - bw / 2), 'y': int(cy - bh / 2), 'w': bw, 'h': bh, 'r': 30, 'a': a, 'b': b})
    return ev, bh


def botao(texto, a, b, cx, cy, periodo=1.0):
    """Pílula de vidro escuro com halo leve, pulsando devagar até o fim."""
    txt = texto.upper()
    esp = 4
    tam, cap, bw, bh = _medidas(txt, 66, W * 0.70, 70, 44, esp)
    raio = bh / 2
    # pulso: cresce 5% e volta, um por período (ritmo da fala)
    pulso = ''
    ms, k, dur, p = 300, 0, (b - a) * 1000, int(periodo * 1000)
    while ms + p <= dur and k < 80:
        pulso += f'\\t({ms},{ms + p // 2},\\fscx105\\fscy105)\\t({ms + p // 2},{ms + p},\\fscx100\\fscy100)'
        ms += p
        k += 1
    ev = []
    x0, y0 = cx - bw / 2, cy - bh / 2
    forma = retangulo(bw, bh, raio)
    org = f'\\org({cx},{cy})'
    ent = '\\fad(250,0)'
    # halo leve (brilho baixo, pulsa junto)
    ev.append(_linha(29, a, b, f'\\an7\\pos({x0:.0f},{y0:.0f}){org}\\1c&HFFFFFF&\\1a{alfa(0.10)}\\bord0\\shad0\\blur26{ent}{pulso}\\p1', forma))
    # sombra
    ev.append(_linha(30, a, b, f'\\an7\\pos({x0:.0f},{y0 + 22:.0f}){org}\\1c&H000000&\\1a{alfa(0.45)}\\bord0\\shad0\\blur24{ent}{pulso}\\p1', forma))
    # película escura
    ev.append(_linha(31, a, b, f'\\an7\\pos({x0:.0f},{y0:.0f}){org}\\1c{cor("#0E1116")}\\1a{alfa(0.48)}\\bord0\\shad0{ent}{pulso}\\p1', forma))
    # reflexo no topo
    ev.append(_linha(32, a, b, f'\\an7\\pos({x0 + 6:.0f},{y0 + 4:.0f}){org}\\1c&HFFFFFF&\\1a{alfa(0.12)}\\bord0\\shad0\\blur7{ent}{pulso}\\p1',
                     retangulo(bw - 12, bh * 0.45, raio - 6)))
    # borda de luz
    ev.append(_linha(33, a, b, f'\\an7\\pos({x0:.0f},{y0:.0f}){org}\\1a&HFF&\\3c&HFFFFFF&\\3a{alfa(0.55)}\\bord1.8\\shad0{ent}{pulso}\\p1', forma))
    # texto
    base = f'\\an5\\fnPoppins\\b1\\fs{tam}\\fsp{esp}\\bord0{org}'
    ev.append(_linha(34, a, b, f'{base}\\pos({cx + 2},{cy + 4})\\1c&H000000&\\1a{alfa(0.4)}\\blur5{ent}{pulso}', esc(txt)))
    ev.append(_linha(35, a, b, f'{base}\\pos({cx},{cy})\\1c&HFFFFFF&{ent}{pulso}', esc(txt)))
    # o desfoque do fundo cobre o tamanho máximo do pulso (borda com degradê)
    m = int(bw * 0.012)
    CAIXAS.append({'x': int(x0) - m, 'y': int(y0) - m, 'w': bw + 2 * m, 'h': bh + 2 * m, 'r': int(raio) + m, 'a': a, 'b': b})
    return ev, bh


def altura(texto, estilo):
    n = len(CAIXAS)
    h = (botao(texto, 0, 1, 0, 0) if estilo == 'botao' else texto_3d(texto, 0, 1, 0, 0))[1]
    del CAIXAS[n:]
    return h


def mascara(caixa, destino):
    """Máscara (branco = vidro) com cantos arredondados e borda levemente esfumada."""
    w, h, r = caixa['w'], caixa['h'], caixa['r']
    im = Image.new('L', (w, h), 0)
    ImageDraw.Draw(im).rounded_rectangle((2, 2, w - 3, h - 3), radius=max(2, min(r, h // 2) - 2), fill=255)
    im.filter(ImageFilter.GaussianBlur(5)).save(destino)


def eh_cta_botao(texto):
    import re
    import unicodedata
    n = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode().lower()
    n = re.sub(r'[^a-z ]+', ' ', n).strip()
    return any(c in n for c in CTA_BOTAO)


def escolher_estilos(destaques):
    out = []
    for d in destaques:
        e = d.get('estilo')
        if e in (None, 'auto', 'cor', 'grande', 'placa', 'carimbo', 'neon', 'faixa', 'dourado', 'vidro'):
            e = '3d'
        out.append(e)
    return out
