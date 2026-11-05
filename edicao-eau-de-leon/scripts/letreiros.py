"""
Letreiros: o destaque de palavra-chave da legenda ("clica em SAIBA MAIS").

A palavra-chave sai da legenda e vira um LETREIRO logo abaixo da frase, no
peito. Cada destaque do vídeo usa um letreiro diferente do anterior (rodízio),
pra não ficar repetitivo. Tudo com as fontes da marca (Bebas Neue, Bungee) e
as cores do logo da Eau de Leon (rosa, azul) + branco, preto e dourado.

  placa    placa rosa da marca, levemente inclinada, cresce da linha;
           letras escuras (Bebas) dão pop
  carimbo  caixa preta inclinada, letras brancas (Bungee); bate na tela
           grande e assenta, como um carimbo
  neon     letras brancas (Bungee) com brilho azul da marca; piscam ao acender
  faixa    marca-texto azul passa da esquerda pra direita; letras brancas (Bebas)
  dourado  letras douradas grandes (Bebas), digitadas letra a letra
  caps     sem letreiro: só CAIXA ALTA dentro da legenda (o jeito dos anúncios
           da marca — use pra nome de perfume: "esse aqui é o CREED AVENTUS")
"""
import os

from PIL import ImageFont

W, H = 1080, 1920
AQUI = os.path.dirname(os.path.abspath(__file__))
FONTES = os.path.normpath(os.path.join(AQUI, '..', 'assets', 'fontes'))

MARCA = {'rosa': '#F2A595', 'azul': '#6BA9CF', 'escuro': '#151A22', 'branco': '#FFFFFF', 'dourado': '#F4C95D'}
RODIZIO = ['placa', 'carimbo', 'neon', 'faixa', 'dourado']

# altura da maiúscula ÷ \fs e largura libass ÷ largura PIL (medidos renderizando)
CAP = {'BebasNeue-Regular.ttf': 0.57, 'Bungee-Regular.ttf': 0.30}
FATOR = {'BebasNeue-Regular.ttf': 0.775, 'Bungee-Regular.ttf': 0.388}
NOME = {'BebasNeue-Regular.ttf': 'Bebas Neue', 'Bungee-Regular.ttf': 'Bungee'}


def cor(hexa):
    r, g, b = (int(hexa[k:k + 2], 16) for k in (1, 3, 5))
    return f'&H{b:02X}{g:02X}{r:02X}&'


def tempo(t):
    t = max(0, t)
    return f'{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}'


def esc(s):
    return s.replace('\\', '\\\\').replace('{', '(').replace('}', ')')


def retangulo(w, h, r):
    """Caminho de desenho ASS: retângulo de cantos arredondados."""
    k = r * 0.45
    return (f'm {r} 0 l {w - r} 0 b {w - k} 0 {w} {k} {w} {r} l {w} {h - r} b {w} {h - k} {w - k} {h} {w - r} {h} '
            f'l {r} {h} b {k} {h} 0 {h - k} 0 {h - r} l 0 {r} b 0 {k} {k} 0 {r} 0')


def largura(texto, arq, tam):
    f = ImageFont.truetype(os.path.join(FONTES, arq), tam)
    b = f.getbbox(texto)
    return (b[2] - b[0]) * FATOR[arq]


def _tamanho(texto, arq, alvo_cap, lim):
    tam = int(alvo_cap / CAP[arq])
    larg = largura(texto, arq, tam)
    if larg > lim:
        tam = int(tam * lim / larg)
        larg = lim
    return tam, larg, tam * CAP[arq]


def _linha(camada, a, b, tags, corpo):
    return f'Dialogue: {camada},{tempo(a)},{tempo(b)},Leg,,0,0,0,,{{{tags}}}{corpo}'


def altura(texto, estilo):
    return gerar(texto, estilo, 0, 1, 0, 0)[1]


def gerar(texto, estilo, a, b, cx, cy):
    """Linhas ASS do letreiro centrado em (cx, cy). Devolve (linhas, altura_px)."""
    txt = texto.upper()
    t = esc(txt)
    ev = []
    saida = '\\fad(0,120)'

    if estilo in ('placa', 'faixa', 'carimbo'):
        arq = 'Bungee-Regular.ttf' if estilo == 'carimbo' else 'BebasNeue-Regular.ttf'
        tam, larg, cap = _tamanho(txt, arq, 74 if estilo == 'carimbo' else 92, W * (0.66 if estilo == 'carimbo' else 0.80))
        padx, pady = 40, 28
        bw, bh = int(larg + 2 * padx), int(cap + 2 * pady)
        caixa = {'placa': MARCA['rosa'], 'faixa': MARCA['azul'], 'carimbo': MARCA['escuro']}[estilo]
        letra = {'placa': MARCA['escuro'], 'faixa': MARCA['branco'], 'carimbo': MARCA['branco']}[estilo]
        gira = {'placa': -2.5, 'faixa': 0, 'carimbo': -5}[estilo]
        engrossa = 1.6 if arq.startswith('Bebas') else 0
        if estilo == 'placa':
            anim_caixa = '\\fscx0\\t(0,160,\\fscx106)\\t(160,230,\\fscx100)'
            anim_txt = ('\\alpha&HFF&\\t(120,121,\\alpha&H00&)\\fscx70\\fscy70'
                        '\\t(120,240,\\fscx104\\fscy104)\\t(240,300,\\fscx100\\fscy100)')
        elif estilo == 'faixa':
            x0, y0 = int(cx - bw / 2), int(cy - bh / 2)
            anim_caixa = (f'\\clip({x0 - 10},{y0 - 10},{x0 - 9},{y0 + bh + 10})'
                          f'\\t(0,260,\\clip({x0 - 10},{y0 - 10},{x0 + bw + 10},{y0 + bh + 10}))')
            anim_txt = '\\alpha&HFF&\\t(160,161,\\alpha&H00&)'
        else:
            anim_caixa = ('\\alpha&HFF&\\t(0,40,\\alpha&H00&)\\fscx122\\fscy122'
                          '\\t(0,140,\\fscx96\\fscy96)\\t(140,200,\\fscx100\\fscy100)')
            anim_txt = anim_caixa
        caminho = retangulo(bw, bh, 18)
        ev.append(_linha(6, a, b, f'\\an5\\pos({cx + 6},{cy + 9})\\frz{gira}\\1c&H000000&\\1a&H70&\\bord0\\shad0\\blur8'
                                   f'{anim_caixa}{saida}\\p1', caminho))
        ev.append(_linha(7, a, b, f'\\an5\\pos({cx},{cy})\\frz{gira}\\1c{cor(caixa)}\\bord0\\shad0{anim_caixa}{saida}\\p1',
                         caminho))
        ev.append(_linha(8, a, b, f'\\an5\\pos({cx},{cy + int(cap * 0.04)})\\frz{gira}\\fn{NOME[arq]}\\b0\\fs{tam}\\fsp1'
                                   f'\\1c{cor(letra)}\\3c{cor(letra)}\\bord{engrossa}\\shad0{anim_txt}{saida}', t))
        return ev, bh

    if estilo == 'neon':
        arq = 'Bungee-Regular.ttf'
        tam, _, cap = _tamanho(txt, arq, 80, W * 0.84)
        pisca = '\\alpha&HFF&\\t(0,30,\\alpha&H00&)\\t(70,100,\\alpha&HA0&)\\t(130,160,\\alpha&H00&)'
        azul = cor(MARCA['azul'])
        for camada, extra in ((6, f'\\bord16\\blur18\\3c{azul}\\1c{azul}'),
                              (7, f'\\bord5\\blur3\\3c{azul}\\1c&HFFFFFF&'),
                              (8, '\\bord0\\1c&HFFFFFF&')):
            ev.append(_linha(camada, a, b, f'\\an5\\pos({cx},{cy})\\fnBungee\\b0\\fs{tam}\\shad0{extra}{pisca}{saida}', t))
        return ev, int(cap * 1.6)

    if estilo == 'dourado':
        arq = 'BebasNeue-Regular.ttf'
        tam, _, cap = _tamanho(txt, arq, 108, W * 0.84)
        passo = 280 / max(1, len(txt))

        def corpo(alfa):
            return ''.join(ch if ch == ' ' else
                           f'{{\\alpha&HFF&\\t({int(i * passo)},{int(i * passo) + 30},\\alpha&H{alfa:02X}&)}}{esc(ch)}'
                           for i, ch in enumerate(txt))
        ev.append(_linha(6, a, b, f'\\an5\\pos({cx + 5},{cy + 9})\\fnBebas Neue\\b0\\fs{tam}\\fsp2\\1c&H000000&\\3c&H000000&'
                                   f'\\bord2.4\\blur7\\shad0{saida}', corpo(0x50)))
        ev.append(_linha(7, a, b, f'\\an5\\pos({cx},{cy})\\fnBebas Neue\\b0\\fs{tam}\\fsp2\\1c{cor(MARCA["dourado"])}'
                                   f'\\3c{cor(MARCA["dourado"])}\\bord2.4\\shad0{saida}', corpo(0)))
        return ev, int(cap * 1.35)

    raise ValueError(f'letreiro desconhecido: {estilo}')


def escolher_estilos(destaques):
    """Rodízio: quem não escolheu estilo recebe o próximo da lista, nunca igual ao anterior."""
    out, k, ant = [], 0, None
    for d in destaques:
        e = d.get('estilo')
        if e in (None, 'auto', 'cor', 'grande'):
            e = RODIZIO[k % len(RODIZIO)]
            k += 1
            if e == ant:
                e = RODIZIO[k % len(RODIZIO)]
                k += 1
        out.append(e)
        ant = e
    return out
