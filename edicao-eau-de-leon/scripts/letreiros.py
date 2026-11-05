"""
Destaques de palavra-chave (o que chama a atenção na legenda).

  3d     a palavra-chave sai da legenda e "pula da tela": letras brancas grossas
         (Bungee) com profundidade 3D (camadas na cor da marca), sombra no chão,
         entrada com giro/salto. Cada destaque varia a cor da profundidade e a
         entrada (rodízio), pra não repetir.
  botao  o "SAIBA MAIS" (e outros CTAs de clique): SEMPRE um botão 3D grande,
         que fica até o fim e PULSA devagar no ritmo da fala, com brilho leve.
         Induz o clique no botão real do anúncio.
  caps   sem efeito: só CAIXA ALTA dentro da legenda (como nos anúncios da
         marca) — use pra nome de perfume ("esse aqui é o CREED AVENTUS").

Fontes e cores da marca (logo): rosa #F2A595, azul #6BA9CF.
"""
import os

from PIL import ImageFont

W, H = 1080, 1920
AQUI = os.path.dirname(os.path.abspath(__file__))
FONTES = os.path.normpath(os.path.join(AQUI, '..', 'assets', 'fontes'))

MARCA = {'rosa': '#F2A595', 'azul': '#6BA9CF', 'escuro': '#151A22', 'branco': '#FFFFFF', 'dourado': '#F4C95D'}
# profundidade (do mais perto ao mais fundo) e entrada de cada variação do 3D
VARIACOES_3D = [
    {'nome': 'azul', 'face': '#FFFFFF', 'fundo': ('#6BA9CF', '#1F4A66'), 'entrada': 'salto'},
    {'nome': 'rosa', 'face': '#FFFFFF', 'fundo': ('#F2A595', '#7A3A2E'), 'entrada': 'giro'},
    {'nome': 'dourado', 'face': '#FFF4D6', 'fundo': ('#F4C95D', '#6B4A12'), 'entrada': 'queda'},
]
CTA_BOTAO = ['saiba mais', 'clique aqui', 'clica aqui', 'link na bio', 'compre agora', 'garanta o seu', 'garante o seu']

CAP = {'BebasNeue-Regular.ttf': 0.57, 'Bungee-Regular.ttf': 0.30}
FATOR = {'BebasNeue-Regular.ttf': 0.775, 'Bungee-Regular.ttf': 0.388}


def cor(hexa):
    r, g, b = (int(hexa[k:k + 2], 16) for k in (1, 3, 5))
    return f'&H{b:02X}{g:02X}{r:02X}&'


def mistura(a, b, f):
    ra, ga, ba = (int(a[k:k + 2], 16) for k in (1, 3, 5))
    rb, gb, bb = (int(b[k:k + 2], 16) for k in (1, 3, 5))
    return '#%02X%02X%02X' % (round(ra + (rb - ra) * f), round(ga + (gb - ga) * f), round(ba + (bb - ba) * f))


def tempo(t):
    t = max(0, t)
    return f'{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}'


def esc(s):
    return s.replace('\\', '\\\\').replace('{', '(').replace('}', ')')


def retangulo(w, h, r):
    k = r * 0.45
    return (f'm {r} 0 l {w - r} 0 b {w - k} 0 {w} {k} {w} {r} l {w} {h - r} b {w} {h - k} {w - k} {h} {w - r} {h} '
            f'l {r} {h} b {k} {h} 0 {h - k} 0 {h - r} l 0 {r} b 0 {k} {k} 0 {r} 0')


def largura(texto, arq, tam):
    f = ImageFont.truetype(os.path.join(FONTES, arq), tam)
    b = f.getbbox(texto)
    return (b[2] - b[0]) * FATOR[arq]


def _linha(camada, a, b, tags, corpo):
    return f'Dialogue: {camada},{tempo(a)},{tempo(b)},Leg,,0,0,0,,{{{tags}}}{corpo}'


def _entrada(tipo):
    if tipo == 'giro':    # gira de lado e assenta
        return '\\fry-70\\fscx60\\fscy60\\t(0,220,\\fry8\\fscx108\\fscy108)\\t(220,320,\\fry0\\fscx100\\fscy100)'
    if tipo == 'queda':   # cai de cima e quica
        return '\\frx-60\\fscx115\\fscy115\\t(0,180,\\frx10\\fscx98\\fscy98)\\t(180,290,\\frx0\\fscx100\\fscy100)'
    return '\\fscx30\\fscy30\\t(0,170,\\fscx118\\fscy118)\\t(170,290,\\fscx100\\fscy100)'  # salto (pop)


def texto_3d(texto, a, b, cx, cy, variacao=0, alvo_cap=88, lim=W * 0.84):
    """Letras grossas com profundidade 3D. Devolve (linhas, altura)."""
    v = VARIACOES_3D[variacao % len(VARIACOES_3D)]
    arq = 'Bungee-Regular.ttf'
    txt = texto.upper()
    tam = int(alvo_cap / CAP[arq])
    larg = largura(txt, arq, tam)
    if larg > lim:
        tam = int(tam * lim / larg)
    cap = tam * CAP[arq]
    prof = max(10, int(cap * 0.30))            # camadas de profundidade (px)
    ent = _entrada(v['entrada'])
    saida = '\\fad(0,140)'
    base = f'\\an5\\fnBungee\\b0\\fs{tam}\\shad0'
    t = esc(txt)
    ev = []
    # sombra no "chão", desfocada
    ev.append(_linha(10, a, b, f'{base}\\pos({cx + prof + 8},{cy + prof + 14})\\1c&H000000&\\1a&H60&\\bord3\\3c&H000000&'
                                f'\\3a&H60&\\blur10{ent}{saida}', t))
    # profundidade: da camada mais funda (escura) até a mais perto (cor da marca)
    for i in range(prof, 0, -1):
        c = mistura(v['fundo'][0], v['fundo'][1], i / prof)
        ev.append(_linha(11, a, b, f'{base}\\pos({cx + i * 0.75:.1f},{cy + i})\\1c{cor(c)}\\bord3\\3c{cor(c)}{ent}{saida}', t))
    # face
    ev.append(_linha(12, a, b, f'{base}\\pos({cx},{cy})\\1c{cor(v["face"])}\\bord3\\3c{cor(v["fundo"][1])}{ent}{saida}', t))
    return ev, int(cap * 1.25 + prof)


def botao(texto, a, b, cx, cy, periodo=1.0):
    """Botão 3D grande ("SAIBA MAIS") que pulsa devagar até o fim do vídeo."""
    arq = 'Bungee-Regular.ttf'
    txt = texto.upper()
    tam = int(66 / CAP[arq])
    larg = largura(txt, arq, tam)
    if larg > W * 0.62:
        tam = int(tam * W * 0.62 / larg)
        larg = W * 0.62
    cap = tam * CAP[arq]
    bw, bh, r = int(larg + 120), int(cap + 78), int((cap + 78) / 2)
    prof = 26
    caminho = retangulo(bw, bh, r)
    # entrada: salta da tela; depois pulsa (cresce 7% e volta) num ritmo de fala
    tags_anim = '\\fscx20\\fscy20\\t(0,200,\\fscx112\\fscy112)\\t(200,320,\\fscx100\\fscy100)'
    ms, k, dur = 520, 0, (b - a) * 1000
    p = int(periodo * 1000)
    while ms + p <= dur and k < 60:
        tags_anim += f'\\t({ms},{ms + p // 2},\\fscx107\\fscy107)\\t({ms + p // 2},{ms + p},\\fscx100\\fscy100)'
        ms += p
        k += 1
    brilho = '\\alpha&HC8&'                     # brilho bem leve (quase transparente)
    ev = []
    ev.append(_linha(20, a, b, f'\\an5\\pos({cx},{cy + prof + 12})\\1c&H000000&\\1a&H50&\\bord0\\shad0\\blur14{tags_anim}\\p1', caminho))
    ev.append(_linha(21, a, b, f'\\an5\\pos({cx},{cy})\\1c&HFFFFFF&{brilho}\\bord10\\3c&HFFFFFF&\\3a&HC8&\\blur12\\shad0{tags_anim}\\p1', caminho))
    ev.append(_linha(22, a, b, f'\\an5\\pos({cx},{cy + prof})\\1c{cor("#4A5560")}\\bord0\\shad0{tags_anim}\\p1', caminho))   # lateral (3D)
    ev.append(_linha(23, a, b, f'\\an5\\pos({cx},{cy})\\1c&HFFFFFF&\\bord3\\3c{cor("#2B323A")}\\shad0{tags_anim}\\p1', caminho))  # face
    ev.append(_linha(24, a, b, f'\\an5\\pos({cx},{cy - bh * 0.22:.0f})\\1c&HFFFFFF&\\bord0\\shad0\\blur6\\alpha&H70&{tags_anim}\\p1',
                     retangulo(int(bw * 0.86), int(bh * 0.32), int(bh * 0.16))))                                           # reflexo
    # texto preto com leve relevo
    base = f'\\an5\\fnBungee\\b0\\fs{tam}\\shad0\\bord0{tags_anim}'
    ev.append(_linha(25, a, b, f'{base}\\pos({cx + 2},{cy + 4})\\1c{cor("#6E7A86")}', esc(txt)))
    ev.append(_linha(26, a, b, f'{base}\\pos({cx},{cy})\\1c{cor(MARCA["escuro"])}', esc(txt)))
    return ev, bh + prof


def altura(texto, estilo):
    if estilo == 'botao':
        return botao(texto, 0, 1, 0, 0)[1]
    return texto_3d(texto, 0, 1, 0, 0)[1]


def eh_cta_botao(texto):
    import re
    import unicodedata
    n = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode().lower()
    n = re.sub(r'[^a-z ]+', ' ', n).strip()
    return any(c in n for c in CTA_BOTAO)


def escolher_estilos(destaques):
    """Sem 'estilo': CTA de clique vira 'botao'; o resto vira 3D (a variação vai em rodízio no render)."""
    out = []
    for d in destaques:
        e = d.get('estilo')
        if e in (None, 'auto', 'cor', 'grande', 'placa', 'carimbo', 'neon', 'faixa', 'dourado'):
            e = '3d'
        out.append(e)
    return out
