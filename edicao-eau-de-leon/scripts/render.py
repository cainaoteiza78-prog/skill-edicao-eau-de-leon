"""
Passo 3 da edição: lê o plano.json (escrito pelo Claude) e renderiza o vídeo
no padrão Eau de Leon.

Uso:
  python render.py <pasta_trabalho>/plano.json [--rapido]

  --rapido   render de rascunho (preset ultrafast) pra conferir antes do final

O que ele faz, na ordem:
  1. corta cada trecho do plano e tira as respirações (silêncios medidos no áudio)
  2. renderiza cada pedaço em 1080x1920 30fps, alternando o enquadramento
     (zoom 1,00 / 1,12) a cada corte seco e aplicando a transição pedida (whip/fade)
  3. junta tudo, põe b-roll, perfumes sem fundo animados, legendas, textos de
     impacto e o cartão final com o logo
  4. áudio: voz limpa e nivelada (-14 LUFS) + trilha opcional que abaixa sozinha

Medidas e estilos: ver ESTILO abaixo e treinamento/02..06. Tudo em px do
quadro 1080x1920.
"""
import sys as _sys
_sys.stdout.reconfigure(encoding='utf-8', errors='replace')  # console do Windows
import argparse
import json
import math
import os
import random
import shutil
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.normpath(os.path.join(AQUI, '..'))
sys.path.insert(0, AQUI)
from catalogo import carregar, por_id, norm  # noqa: E402
from cortes import energia_db, pedacos_do_trecho  # noqa: E402
from textos import montar_ass, rotulo_png  # noqa: E402
from enquadramento import altura_legenda  # noqa: E402

W, H, FPS = 1080, 1920, 30

# ── Medidas tiradas dos reels da @eau.de.leon (ver treinamento/01) ──────────
ESTILO = {
    # textos (fontes, tamanhos, sombras): ver textos.py → ESTILO_TEXTO
    'legenda': {'max_palavras': 4, 'max_chars': 24},
    'perfume': {'altura': 300, 'altura_grande': 460, 'base_y': 1420, 'largura_linha': 940, 'slot_max': 250},
    'zoom_corte': 1.12,
    'cartao_final': {'duracao': 2.0, 'dissolve': 0.45, 'logo_largura': 560, 'logo_y': 768},
    'musica_volume': 0.12,
    'whip': 0.10,
}

FONTES = os.path.join(RAIZ, 'assets', 'fontes')
LOGO = os.path.join(RAIZ, 'assets', 'logo', 'eau-de-leon-branco.png')
PERFUMES = os.path.join(RAIZ, 'assets', 'perfumes')
MUSICAS = os.path.join(RAIZ, 'assets', 'musicas')


def ff(args, cwd):
    r = subprocess.run(['ffmpeg', '-y', '-hide_banner', '-v', 'error'] + args, cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f'ffmpeg falhou:\n{" ".join(args)[:1500]}\n{r.stderr[-2500:]}')


# ── 1/2. cortes (ver cortes.py) → segmentos ─────────────────────────────────
def montar_segmentos(plano, trans, energias):
    segs, removidas = [], []
    for cena, tr in enumerate(plano['trechos']):
        k = tr['take']
        take = trans['takes'][k - 1]
        ini, fim = max(0.0, tr['ini']), min(take['duracao'], tr['fim'])
        if fim - ini < 0.15:
            continue
        db, voz = energias[k - 1]
        pedacos, fora = pedacos_do_trecho(take['palavras'], db, voz, ini, fim, take['duracao'], tr.get('manter_pausas', False))
        removidas += [{'take': k, 'ini': p['ini'], 'p': p['p']} for p in fora]
        primeiro = True
        for i, (a, b) in enumerate(pedacos):
            zoom = tr.get('zoom') or (ESTILO['zoom_corte'] if i % 2 == 1 else 1.0)
            segs.append({'take': k, 'a': a, 'b': b, 'cena': cena, 'abre': primeiro,
                         'transicao': tr.get('transicao', 'corte') if primeiro else 'corte',
                         'zoom': zoom, 'foco_x': tr.get('foco_x', 0.5), 'foco_y': tr.get('foco_y', 0.5)})
            primeiro = False
    # nunca repetir o mesmo trecho da take (trechos do plano encostados)
    for i in range(1, len(segs)):
        p, s = segs[i - 1], segs[i]
        if p['take'] == s['take'] and s['a'] < p['b'] and s['b'] > p['a']:
            s['a'] = p['b']
    segs = [s for s in segs if s['b'] - s['a'] >= 0.1]
    t = 0.0
    for s in segs:
        s['dst'] = t
        t += s['b'] - s['a']
    return segs, t, removidas


def mapear(segs, take, t, depois=True):
    """Tempo da take → tempo no vídeo final. Se caiu num pedaço cortado, vai pro próximo."""
    for s in segs:
        if s['take'] == take and s['a'] - 0.001 <= t <= s['b'] + 0.001:
            return s['dst'] + (t - s['a'])
    cand = [s for s in segs if s['take'] == take and s['a'] > t]
    if depois and cand:
        return min(cand, key=lambda s: s['a'])['dst']
    cand = [s for s in segs if s['take'] == take and s['b'] < t]
    if cand:
        s = max(cand, key=lambda s: s['b'])
        return s['dst'] + (s['b'] - s['a'])
    return None


def filtro_video(s, prox_whip):
    z = s['zoom']
    par = lambda v: int(math.ceil(v / 2) * 2)
    w, h = par(W * z), par(H * z)
    x = f"(iw-{W})*{s['foco_x']}"
    y = f"(ih-{H})*{s['foco_y']}"
    f = [f'scale={w}:{h}:force_original_aspect_ratio=increase', f'crop={W}:{H}:{x}:{y}', 'setsar=1', f'fps={FPS}']
    d = s['b'] - s['a']
    wp = ESTILO['whip']
    if s['abre'] and s['transicao'] == 'whip':
        f.append(f"avgblur=sizeX=70:sizeY=1:enable='lt(t,{wp * 0.7:.3f})'")
        f.append(f"avgblur=sizeX=28:sizeY=1:enable='between(t,{wp * 0.7:.3f},{wp:.3f})'")
    elif s['abre'] and s['transicao'] == 'fade':
        f.append('fade=t=in:st=0:d=0.25')
    elif s['abre'] and s['transicao'] == 'flash':
        f.append('fade=t=in:st=0:d=0.18:color=white')
    if prox_whip:
        f.append(f"avgblur=sizeX=60:sizeY=1:enable='gte(t,{max(0, d - 0.04):.3f})'")
    f.append('format=yuv420p')
    return ','.join(f)


# ── 3. legenda ──────────────────────────────────────────────────────────────
def palavras_finais(plano, trans, segs):
    # cada palavra vai pro pedaço com quem ela mais se sobrepõe (o tempo do
    # Whisper pode cair parte num silêncio que foi cortado — a palavra continua lá)
    out = []
    for k, take in enumerate(trans['takes'], 1):
        meus = [s for s in segs if s['take'] == k]
        for p in take['palavras']:
            melhor, sob = None, 0.0
            for s in meus:
                o = min(s['b'], p['fim']) - max(s['a'], p['ini'])
                if o > sob:
                    melhor, sob = s, o
            if melhor is None or sob < 0.04:
                continue
            s = melhor
            out.append({'p': p['p'], 'take': k, 'src': p['ini'],
                        'ini': s['dst'] + max(0.0, p['ini'] - s['a']),
                        'fim': s['dst'] + min(s['b'], p['fim']) - s['a']})
    out.sort(key=lambda w: w['ini'])
    # o Whisper separa símbolo da palavra ("10", "%"): junta de volta → "10%"
    juntas = []
    for w in out:
        if juntas and w['p'].strip() and not any(ch.isalnum() for ch in w['p']) and w['p'].strip()[0] in '%$€+°ºª':
            juntas[-1] = juntas[-1] | {'p': juntas[-1]['p'].rstrip() + w['p'].strip(), 'fim': w['fim']}
        else:
            juntas.append(w)
    out = juntas
    # correções: "de" pode ser frase (várias palavras) → vira uma palavra só
    for c in plano.get('correcoes', []):
        de = norm(c['de']).split()
        if not de:
            continue
        i = 0
        while i < len(out):
            seq = []
            j = i
            while j < len(out) and len(seq) < len(de):
                seq += norm(out[j]['p']).split()
                j += 1
            if seq == de:
                pont = out[j - 1]['p'][-1] if out[j - 1]['p'][-1] in '?!.,' else ''
                out[i] = out[i] | {'p': c['para'] + pont, 'fim': out[j - 1]['fim']}
                del out[i + 1:j]
            i += 1
    return out


def limpar(tok):
    t = tok.strip().strip('"“”«»')
    while t and t[-1] in ',.;:…':
        t = t[:-1]
    return t


def blocos_legenda(plano, words):
    modo = plano.get('legenda', 'frase')
    if modo == 'nenhuma':
        return []
    E = ESTILO['legenda']
    manter = {'Eau', 'Leon', 'Leon.'}
    for c in plano.get('correcoes', []):
        manter.update(c['para'].split())
    maiusc = []
    for m in plano.get('legenda_maiusculas', []):
        a = plano['_map'](m['take'], m['ini'])
        b = plano['_map'](m['take'], m['fim'], False)
        if a is not None and b is not None:
            maiusc.append((a - 0.01, b + 0.01))

    def fmt(w, inicio_frase):
        t = limpar(w['p'])
        if inicio_frase and t[:1].isupper() and t not in manter and not any(ch.isdigit() for ch in t):
            if not (len(t) > 1 and t.isupper()):  # sigla fica
                t = t[:1].lower() + t[1:]
        if any(a <= w['ini'] <= b for a, b in maiusc):
            t = t.upper()
        return t

    blocos, cur = [], []
    fim_frase = True
    for i, w in enumerate(words):
        prev = words[i - 1] if i else None
        novo = not cur
        if cur:
            txt = ' '.join(x['t'] for x in cur)
            if modo == 'palavra' or len(cur) >= E['max_palavras'] or len(txt) + 1 + len(limpar(w['p'])) > E['max_chars'] \
                    or w['ini'] - prev['fim'] > 0.35 or prev['p'].rstrip()[-1:] in '.?!' \
                    or (prev['p'].rstrip()[-1:] in ',;:' and len(cur) >= 2):
                blocos.append(cur)
                cur, novo = [], True
        cur.append({'t': fmt(w, fim_frase), 'ini': w['ini'], 'fim': w['fim']})
        fim_frase = w['p'].rstrip()[-1:] in '.?!'
    if cur:
        blocos.append(cur)
    out = []
    for i, b in enumerate(blocos):
        ini = b[0]['ini']
        prox = blocos[i + 1][0]['ini'] if i + 1 < len(blocos) else None
        fim = prox if prox is not None and prox - b[-1]['fim'] < 0.5 else b[-1]['fim'] + 0.25
        out.append({'texto': ' '.join(x['t'] for x in b if x['t']), 'ini': ini, 'fim': max(fim, ini + 0.25)})
    return out


# ── 4. perfumes e b-roll ────────────────────────────────────────────────────
def png_perfume(origem, destino, larg_max, alt_max):
    """Frasco redimensionado, sem sombra (nos reels o frasco entra "chapado")."""
    im = Image.open(origem).convert('RGBA')
    f = min(larg_max / im.width, alt_max / im.height)
    im = im.resize((max(1, round(im.width * f)), max(1, round(im.height * f))), Image.LANCZOS)
    im.save(destino)
    return im.size, 0


def expr_anim(anim, A, x0, y0, lado):
    """Expressões x,y do overlay. p = progresso 0..1 com ease-out cúbico."""
    def p(d):
        return f'(1-pow(1-clip((t-{A:.3f})/{d},0,1),3))'
    if anim == 'drop':
        return f'{x0}', f'{y0}-220*(1-{p(0.30)})'
    if anim == 'slide':
        dx = -700 if lado < 0 else 700
        return f'{x0}+({dx})*(1-{p(0.32)})', f'{y0}'
    if anim == 'fade':
        return f'{x0}', f'{y0}'
    return f'{x0}', f'{y0}+22*(1-{p(0.14)})'  # pop (padrão)


def entrada_anim(anim):
    return {'fade': 0.30, 'drop': 0.12, 'slide': 0.12}.get(anim, 0.10)


def preparar_perfumes(plano, trabalho, total, cat, y_legenda=1080):
    P = ESTILO['perfume']
    itens = []
    grupos = plano.get('perfumes', [])
    inicios = []
    for g in grupos:
        ts = [plano['_map'](i['take'], i['t']) for i in g['itens']]
        inicios.append(min(x for x in ts if x is not None) if any(x is not None for x in ts) else None)
    for gi, g in enumerate(grupos):
        n = len(g['itens'])
        grande = g.get('tamanho') == 'grande'
        alt = P['altura_grande'] if grande else (P['altura'] if n <= 3 else int(P['altura'] * 0.9))
        slot = min(P['slot_max'] * (1.5 if grande else 1), P['largura_linha'] / n)
        prox = next((x for x in inicios[gi + 1:] if x is not None), None)
        fim_g = None
        if g.get('ate'):
            fim_g = plano['_map'](g['ate']['take'], g['ate']['t'])
        for i, it in enumerate(g['itens']):
            p = por_id(cat, it['id'])
            if not p:
                raise SystemExit(f"Perfume '{it['id']}' não está no catálogo. Use: python scripts/catalogo.py buscar \"nome\"")
            A = plano['_map'](it['take'], it['t'])
            if A is None:
                continue
            B = fim_g or (min(prox, A + 3.5 + (n - 1 - i) * 0.5) if prox else None)
            B = min(B or total, total)
            if B - A < 0.3:
                continue
            arq = os.path.join(trabalho, f'perf_{gi}_{i}.png')
            (tw, th), m = png_perfume(os.path.join(PERFUMES, p['arquivo']), arq, slot - 12, alt)
            cx = W / 2 + (i - (n - 1) / 2) * slot
            # fileira logo abaixo da legenda (que fica na altura do peito)
            base_auto = min(1800, max(P['base_y'], y_legenda + 70 + alt))
            base = int(g['base_y'] * H) if 'base_y' in g else base_auto
            x0, y0 = int(cx - tw / 2), int(base - th + m)
            if 'x' in it:
                x0 = int(it['x'] * W - tw / 2)
            if 'y' in it:
                y0 = int(it['y'] * H - th / 2)
            anim = it.get('animacao', g.get('animacao', 'pop'))
            itens.append({'png': arq, 'A': A, 'B': B, 'x0': x0, 'y0': y0, 'anim': anim, 'lado': -1 if cx < W / 2 else 1})
    return itens


def preparar_rotulos(textos, tmp):
    """Rótulos (texto nativo TikTok com emoji) viram PNG e entram por overlay."""
    out = []
    for k, t in enumerate(x for x in textos if x['estilo'] == 'rotulo'):
        png = os.path.join(tmp, f'rotulo_{k}.png')
        w, h = rotulo_png(t['texto'], png, t.get('tamanho'))
        cx, cy = t.get('x', 0.5) * W, t.get('y', 0.14) * H
        out.append({'png': png, 'A': t['ini'], 'B': t['fim'], 'x': int(cx - w / 2), 'y': int(cy - h / 2)})
    return out


def preparar_broll(plano, trabalho, total):
    out = []
    for i, b in enumerate(plano.get('broll', [])):
        A = plano['_map'](b['take'], b['ini'])
        B = plano['_map'](b['take'], b['fim'], False)
        if A is None or B is None or B - A < 0.3:
            continue
        arq = b['arquivo']
        if not os.path.isabs(arq):
            arq = os.path.normpath(os.path.join(trabalho, arq))
        if not os.path.exists(arq):
            raise SystemExit(f'b-roll não encontrado: {arq}')
        video = arq.lower().endswith(('.mp4', '.mov', '.mkv', '.webm', '.m4v'))
        out.append({'arq': arq, 'A': A, 'B': min(B, total), 'video': video, 'inicio': b.get('inicio_arquivo', 0.0),
                    'transicao': b.get('transicao', 'whip'), 'foco_x': b.get('foco_x', 0.5)})
    return out


# ── 5. principal ────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('plano')
    ap.add_argument('--rapido', action='store_true')
    a = ap.parse_args()

    plano_path = os.path.abspath(a.plano)
    trabalho = os.path.dirname(plano_path)
    plano = json.load(open(plano_path, encoding='utf8'))
    trans = json.load(open(os.path.join(trabalho, 'transcricao.json'), encoding='utf8'))
    cat = carregar()
    tmp = os.path.join(trabalho, '_render')
    os.makedirs(tmp, exist_ok=True)

    energias = [energia_db(os.path.join(trabalho, f"take{t['n']}.wav")) for t in trans['takes']]
    segs, total, bastidor = montar_segmentos(plano, trans, energias)
    if not segs:
        raise SystemExit('Plano sem trechos válidos.')
    plano['_map'] = lambda take, t, depois=True: mapear(segs, take, t, depois)
    print(f'{len(segs)} pedaços, {total:.1f}s de fala editada', flush=True)
    if bastidor:
        print('fala de bastidor removida: ' + ' | '.join(f"take {b['take']} {b['ini']:.2f}s \"{b['p']}\"" for b in bastidor), flush=True)
    # legenda abaixo do pescoço, na altura do peito (rosto detectado)
    if plano.get('legenda_y'):
        y_legenda, rostos = int(plano['legenda_y'] * H), []
    else:
        y_legenda, rostos = altura_legenda(segs, trans['takes'])
    print(f'legenda em y={y_legenda} ({len(rostos)} rosto(s) detectado(s))', flush=True)

    preset = 'ultrafast' if a.rapido else 'veryfast'
    lista = []
    for i, s in enumerate(segs):
        prox_whip = i + 1 < len(segs) and segs[i + 1]['abre'] and segs[i + 1]['transicao'] == 'whip'
        arq = os.path.join(tmp, f'seg{i:03d}.mkv')
        d = s['b'] - s['a']
        fade_out = max(0, d - 0.03)
        ff(['-ss', f"{s['a']:.3f}", '-i', trans['takes'][s['take'] - 1]['arquivo'], '-t', f'{d:.3f}',
            '-filter_complex', f"[0:v]{filtro_video(s, prox_whip)}[v];[0:a]aresample=48000,aformat=channel_layouts=stereo,afade=t=in:d=0.02,afade=t=out:st={fade_out:.3f}:d=0.03[a]",
            '-map', '[v]', '-map', '[a]', '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '14', '-c:a', 'pcm_s16le', arq], tmp)
        lista.append(f"file '{os.path.basename(arq)}'")
        print(f'  pedaço {i + 1}/{len(segs)}', flush=True)
    with open(os.path.join(tmp, 'lista.txt'), 'w') as f:
        f.write('\n'.join(lista))
    ff(['-f', 'concat', '-safe', '0', '-i', 'lista.txt', '-c', 'copy', 'junto.mkv'], tmp)

    # textos de tela (tempo final)
    textos = []
    for t in plano.get('textos', []):
        A = plano['_map'](t['take'], t['ini'])
        B = plano['_map'](t['take'], t['fim'], False)
        if A is None or B is None:
            continue
        textos.append(t | {'ini': A, 'fim': max(B, A + 0.6)})
    words = palavras_finais(plano, trans, segs)
    legendas = blocos_legenda(plano, words)
    # legenda some enquanto texto de impacto/destaque está na tela
    bloqueios = [(t['ini'], t['fim']) for t in textos if t['estilo'] in ('impacto', 'destaque')]
    leg_ok = []
    for l in legendas:
        for a0, b0 in bloqueios:  # começou durante o texto grande: espera ele sair
            if a0 - 0.05 <= l['ini'] < b0:
                l['ini'] = b0 + 0.02
        for a0, b0 in bloqueios:
            if l['ini'] < a0 < l['fim']:
                l['fim'] = a0
        if l['fim'] - l['ini'] >= 0.15:
            leg_ok.append(l)
    with open(os.path.join(tmp, 'legenda.ass'), 'w', encoding='utf8') as f:
        f.write(montar_ass(leg_ok, textos, y_legenda))
    with open(os.path.join(trabalho, 'legenda.srt'), 'w', encoding='utf8') as f:
        for i, l in enumerate(leg_ok, 1):
            ts = lambda x: f'{int(x // 3600):02d}:{int(x % 3600 // 60):02d}:{int(x % 60):02d},{int(round(x % 1 * 1000)) % 1000:03d}'
            f.write(f"{i}\n{ts(l['ini'])} --> {ts(l['fim'])}\n{l['texto']}\n\n")
    fdir = os.path.join(tmp, 'fonts')
    os.makedirs(fdir, exist_ok=True)
    for fn in os.listdir(FONTES):
        if fn.endswith('.ttf'):
            shutil.copy(os.path.join(FONTES, fn), fdir)

    cartao = plano.get('cartao_final', plano.get('formato', 'leo') == 'leo')
    C = ESTILO['cartao_final']
    final = total + (C['duracao'] if cartao else 0.0)

    perfumes = preparar_perfumes(plano, tmp, total, cat, y_legenda)
    rotulos = preparar_rotulos(textos, tmp)
    brolls = preparar_broll(plano, trabalho, total)

    entradas = ['-i', 'junto.mkv']
    grafo = []
    cur = '[0:v]'
    idx = 1
    for k, b in enumerate(brolls):
        d = b['B'] - b['A']
        if b['video']:
            entradas += ['-ss', f"{b['inicio']:.3f}", '-t', f'{d + 0.1:.3f}', '-i', b['arq']]
        else:
            entradas += ['-loop', '1', '-framerate', str(FPS), '-t', f'{d + 0.1:.3f}', '-i', b['arq']]
        filtros = [f'scale={W}:{H}:force_original_aspect_ratio=increase', f"crop={W}:{H}:(iw-{W})*{b['foco_x']}:(ih-{H})/2",
                   'setsar=1', f'fps={FPS}', 'format=yuv420p', f"setpts=PTS-STARTPTS+{b['A']:.3f}/TB"]
        if b['transicao'] == 'whip':
            filtros.append(f"avgblur=sizeX=70:sizeY=1:enable='between(t,{b['A']:.3f},{b['A'] + ESTILO['whip']:.3f})'")
        grafo.append(f'[{idx}:v]{",".join(filtros)}[br{k}]')
        xexpr = '0'
        if b['transicao'] == 'slide':
            xexpr = f"-{W}*(1-(1-pow(1-clip((t-{b['A']:.3f})/0.3,0,1),3)))"
        grafo.append(f"{cur}[br{k}]overlay=x='{xexpr}':y=0:enable='between(t,{b['A']:.3f},{b['B']:.3f})':eof_action=pass[vb{k}]")
        cur = f'[vb{k}]'
        idx += 1
    for k, p in enumerate(perfumes):
        entradas += ['-loop', '1', '-framerate', str(FPS), '-t', f"{p['B'] + 0.2:.3f}", '-i', os.path.basename(p['png'])]
        din = entrada_anim(p['anim'])
        grafo.append(f"[{idx}:v]format=rgba,fade=t=in:st={p['A']:.3f}:d={din}:alpha=1,fade=t=out:st={max(p['A'], p['B'] - 0.12):.3f}:d=0.12:alpha=1[pf{k}]")
        x, y = expr_anim(p['anim'], p['A'], p['x0'], p['y0'], p['lado'])
        grafo.append(f"{cur}[pf{k}]overlay=x='{x}':y='{y}':enable='between(t,{p['A']:.3f},{p['B']:.3f})':eof_action=pass[vp{k}]")
        cur = f'[vp{k}]'
        idx += 1
    for k, r in enumerate(rotulos):
        entradas += ['-loop', '1', '-framerate', str(FPS), '-t', f"{r['B'] + 0.2:.3f}", '-i', os.path.basename(r['png'])]
        grafo.append(f"[{idx}:v]format=rgba,fade=t=in:st={r['A']:.3f}:d=0.15:alpha=1,fade=t=out:st={max(r['A'], r['B'] - 0.15):.3f}:d=0.15:alpha=1[rt{k}]")
        grafo.append(f"{cur}[rt{k}]overlay=x={r['x']}:y={r['y']}:enable='between(t,{r['A']:.3f},{r['B']:.3f})':eof_action=pass[vr{k}]")
        cur = f'[vr{k}]'
        idx += 1
    for k, dv in enumerate(plano.get('divisorias', [])):
        A = plano['_map'](dv['take'], dv['ini'])
        B = plano['_map'](dv['take'], dv['fim'], False)
        if A is None or B is None:
            continue
        y0, y1 = int(dv.get('y0', 0.23) * H), int(dv.get('y1', 0.62) * H)
        grafo.append(f"{cur}drawbox=x={W // 2 - 3}:y={y0}:w=6:h={y1 - y0}:color=white@1:t=fill:enable='between(t,{A:.3f},{B:.3f})'[vd{k}]")
        cur = f'[vd{k}]'
    grafo.append(f"{cur}ass=legenda.ass:fontsdir=fonts[vt]")
    cur = '[vt]'
    if cartao:
        # cartão: fundo preto + logo branco, dissolvendo por cima do último quadro
        card = os.path.join(tmp, 'cartao.png')
        logo = Image.open(LOGO).convert('RGBA')
        f = C['logo_largura'] / logo.width
        logo = logo.resize((C['logo_largura'], round(logo.height * f)), Image.LANCZOS)
        fundo = Image.new('RGBA', (W, H), (3, 3, 5, 255))
        fundo.alpha_composite(logo, ((W - logo.width) // 2, C['logo_y'] - logo.height // 2))
        fundo.save(card)
        entradas += ['-loop', '1', '-framerate', str(FPS), '-t', f'{final + 0.2:.3f}', '-i', 'cartao.png']
        grafo.append(f"{cur}tpad=stop_mode=clone:stop_duration={C['duracao']}[vpad]")
        grafo.append(f"[{idx}:v]format=rgba,fade=t=in:st={total:.3f}:d={C['dissolve']}:alpha=1[card]")
        grafo.append(f"[vpad][card]overlay=0:0:enable='gte(t,{total:.3f})'[vout]")
        idx += 1
    else:
        grafo.append(f'{cur}null[vout]')

    musica = plano.get('musica')
    if musica == 'auto':
        cand = sorted(f for f in os.listdir(MUSICAS) if f.lower().endswith(('.mp3', '.wav', '.m4a'))) if os.path.isdir(MUSICAS) else []
        musica = os.path.join(MUSICAS, cand[0]) if cand else None
    # Loudnorm em 2 passadas: mede a voz editada e aplica a correção exata (-14 LUFS).
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', 'junto.mkv', '-vn', '-af',
                        'highpass=f=80,loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'],
                       cwd=tmp, capture_output=True, text=True)
    try:
        m = json.loads(r.stderr[r.stderr.rindex('{'):r.stderr.rindex('}') + 1])
        ln = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
              f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    except (ValueError, KeyError):
        ln = 'loudnorm=I=-14:TP=-1.5:LRA=11'
    voz = f'[0:a]highpass=f=80,{ln},aresample=48000,apad=whole_dur={final:.3f}'
    if musica:
        entradas += ['-stream_loop', '-1', '-i', musica]
        grafo.append(f'{voz},asplit=2[voz][chave]')
        grafo.append(f"[{idx}:a]aresample=48000,aformat=channel_layouts=stereo,volume={ESTILO['musica_volume']},afade=t=in:d=0.8,afade=t=out:st={max(0, final - 1.5):.3f}:d=1.5[mus]")
        grafo.append('[mus][chave]sidechaincompress=threshold=0.02:ratio=6:attack=30:release=500[duck]')
        grafo.append('[voz][duck]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[aout]')
    else:
        grafo.append(f'{voz}[aout]')

    saida = plano.get('saida', 'editado.mp4')
    if not os.path.isabs(saida):
        saida = os.path.join(trabalho, saida)
    with open(os.path.join(tmp, 'grafo.txt'), 'w', encoding='utf8') as f:
        f.write(';\n'.join(grafo))
    cmd = entradas + ['-filter_complex_script', 'grafo.txt', '-map', '[vout]', '-map', '[aout]', '-t', f'{final:.3f}',
                      '-c:v', 'libx264', '-preset', preset, '-crf', '18', '-pix_fmt', 'yuv420p', '-r', str(FPS),
                      '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart']
    try:
        ff(cmd + [saida], tmp)
    except SystemExit:
        # PC com pouca memória: o x264 pode falhar ao alocar; tenta de novo mais leve.
        print('encoder falhou; tentando de novo com menos threads...', flush=True)
        ff(cmd + ['-threads', '2', '-x264-params', 'rc-lookahead=10', saida], tmp)

    resumo = {
        'saida': saida, 'duracao': round(final, 2), 'fala': round(total, 2), 'pedacos': len(segs),
        'legendas': len(leg_ok), 'textos': [{'texto': t['texto'], 'ini': round(t['ini'], 2), 'fim': round(t['fim'], 2)} for t in textos],
        'perfumes': [{'png': os.path.basename(p['png']), 'ini': round(p['A'], 2), 'fim': round(p['B'], 2)} for p in perfumes],
        'broll': [{'arquivo': os.path.basename(b['arq']), 'ini': round(b['A'], 2), 'fim': round(b['B'], 2)} for b in brolls],
        'cortes': [round(s['dst'], 2) for s in segs],
        'legenda_y': y_legenda, 'rostos': rostos,
        'bastidor_removido': bastidor,
    }
    with open(os.path.join(trabalho, 'linha_do_tempo.json'), 'w', encoding='utf8') as f:
        json.dump(resumo, f, ensure_ascii=False, indent=1)
    print(f'PRONTO: {saida} ({final:.1f}s). Linha do tempo em linha_do_tempo.json')


if __name__ == '__main__':
    main()
