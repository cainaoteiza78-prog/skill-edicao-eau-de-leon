"""
Cortes: tira respirações, pausas e falas de bastidor ("corta", "vai", "parou"...).

O corte é guiado pelas PALAVRAS (tempo do Whisper) e refinado pela ENERGIA do
áudio: cada palavra vira o trecho em que a voz está realmente forte em volta
dela. Tudo entre uma palavra e a próxima que não for voz forte (respiração,
pausa, estalo de boca) sai. Respiração tem energia, mas é bem mais fraca que a
voz — por isso o limiar é relativo ao volume da própria pessoa.
"""
import re
import unicodedata
import wave

import numpy as np

PASSO = 0.01  # energia medida a cada 10 ms

# Folgas (s) que ficam em volta da voz em cada corte.
FOLGA_INICIO = 0.03
FOLGA_FIM = 0.05
JUNTA_SE_GAP = 0.04     # buraco menor que isso entre palavras não é corte
PEDACO_MINIMO = 0.18

# Falas de bastidor. Só saem quando estão ISOLADAS (pausa antes ou depois, ou
# na ponta da take) e a "frase" inteira é só disso — "vai ficar lindo" fica.
BASTIDOR = {
    'corta', 'corte', 'cortar', 'cortou', 'vai', 'vai la', 'parou', 'para', 'pera', 'perai', 'espera',
    'de', 'novo', 'denovo', 'repete', 'repetir', 'repetindo', 'vou', 'errei', 'erro', 'droga', 'nossa',
    'gravando', 'grava', 'gravou', 'valendo', 'acao', 'ok', 'okay', 'beleza', 'bora', 'pronto', 'foi',
    'ta', 'tá', 'e', 'ai', 'aí', 'um', 'dois', 'tres', '1', '2', '3', 'again', 'calma', 'deixa', 'eu',
    'ver', 'hum', 'hm', 'ah', 'eh', 'é', 'uh', 'tipo', 'entao', 'então', 'assim', 'mais', 'uma', 'vez',
    'comecar', 'começar', 'comeco', 'começo', 'desde', 'o', 'do',
}
# Pelo menos uma destas tem que estar no trecho isolado pra ele ser bastidor
# (evita apagar um "e aí" ou "então" que é parte da fala).
FORTES = {'corta', 'corte', 'cortar', 'cortou', 'vai', 'parou', 'pera', 'perai', 'espera', 'novo', 'denovo',
          'repete', 'repetir', 'repetindo', 'errei', 'gravando', 'grava', 'gravou', 'valendo', 'acao',
          'ok', 'okay', 'bora', 'droga', 'again', 'calma', 'hum', 'hm', 'uh', 'eh', 'ah', 'vez'}
PAUSA_ISOLA = 0.30


def _n(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()


def energia_db(wav_path):
    """dBFS a cada 10 ms + o nível típico da voz (percentil 90)."""
    with wave.open(wav_path) as w:
        sr = w.getframerate()
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32)
    jan = int(sr * PASSO)
    n = len(x) // jan
    rms = np.sqrt((x[: n * jan].reshape(n, jan) ** 2).mean(axis=1) + 1e-9)
    db = np.clip(20 * np.log10(rms / 32768 + 1e-9), -90, 0)
    return db, float(np.percentile(db, 90))


def eh_bastidor(palavras, i, j, ini_trecho, fim_trecho):
    """palavras[i:j] é uma fala de bastidor isolada?"""
    toks = [t for p in palavras[i:j] for t in _n(p['p']).split()]
    if not toks or len(toks) > 6:
        return False
    if not all(t in BASTIDOR for t in toks) or not any(t in FORTES for t in toks):
        return False
    antes = palavras[i]['ini'] - (palavras[i - 1]['fim'] if i > 0 else ini_trecho)
    depois = (palavras[j]['ini'] if j < len(palavras) else fim_trecho) - palavras[j - 1]['fim']
    return antes >= PAUSA_ISOLA or depois >= PAUSA_ISOLA or i == 0 or j == len(palavras)


def tirar_bastidor(palavras, ini_trecho, fim_trecho):
    """Remove grupos curtos de falas de bastidor. Devolve (mantidas, removidas)."""
    # agrupa por pausa: cada grupo é uma "frase" falada de uma vez
    grupos, cur = [], []
    for k, p in enumerate(palavras):
        if cur and p['ini'] - palavras[k - 1]['fim'] >= PAUSA_ISOLA:
            grupos.append(cur)
            cur = []
        cur.append(k)
    if cur:
        grupos.append(cur)
    fora = set()
    for g in grupos:
        # o grupo inteiro, ou o começo/fim dele ("corta, vai: Se você ama...")
        i0, j0 = g[0], g[-1] + 1
        if eh_bastidor(palavras, i0, j0, ini_trecho, fim_trecho):
            fora.update(range(i0, j0))
            continue
        for corte in range(1, min(5, len(g))):
            if eh_bastidor(palavras, i0, i0 + corte, ini_trecho, fim_trecho) and \
                    palavras[i0 + corte]['ini'] - palavras[i0 + corte - 1]['fim'] >= 0.15:
                fora.update(range(i0, i0 + corte))
    return [p for k, p in enumerate(palavras) if k not in fora], [p for k, p in enumerate(palavras) if k in fora]


def borda_da_voz(db, voz, ini, fim, dur, lim_esq=None, lim_dir=None):
    """Início/fim reais da voz de UMA palavra (o Whisper erra por décimos e às
    vezes estica a palavra por cima da pausa). Só anda por voz contígua e nunca
    invade a palavra vizinha (lim_esq = fim da anterior, lim_dir = início da próxima)."""
    forte = voz - 18
    n = len(db)
    lo = int(max(0.0, ini - 0.12, lim_esq if lim_esq is not None else 0.0) / PASSO)
    hi = int(min(dur, fim + 0.20, lim_dir if lim_dir is not None else dur) / PASSO)
    hi = min(hi, n)
    nucleo = [k for k in range(int(ini / PASSO), min(int(fim / PASSO) + 1, hi)) if k < n and db[k] > forte]
    if not nucleo:
        return max(0.0, ini - FOLGA_INICIO), min(dur, fim + FOLGA_FIM)
    s, e = nucleo[0], nucleo[-1]
    # dentro do intervalo do Whisper, a voz real termina no último trecho forte
    # que não esteja separado do núcleo por > 120 ms de fraco
    k = nucleo[0]
    ultimo = k
    while k < min(int(fim / PASSO) + 1, hi):
        if db[k] > forte:
            ultimo = k
        elif k - ultimo > 12:
            break
        k += 1
    e = ultimo
    while e + 1 < hi and db[e + 1] > forte:   # estende enquanto for voz
        e += 1
    while s - 1 >= lo and db[s - 1] > forte:
        s -= 1
    return max(0.0, s * PASSO - FOLGA_INICIO), min(dur, (e + 1) * PASSO + FOLGA_FIM)


def pedacos_do_trecho(palavras_take, db, voz, ini, fim, dur, manter_pausas=False):
    """[(a,b), ...] dentro de [ini,fim] da take, só com voz, sem bastidor nem respiração."""
    pal = [p for p in palavras_take if ini - 0.05 <= (p['ini'] + p['fim']) / 2 <= fim + 0.05]
    if not pal:
        return [(ini, fim)], []
    pal, removidas = tirar_bastidor(pal, ini, fim)
    if not pal:
        return [], removidas
    if manter_pausas:
        a, _ = borda_da_voz(db, voz, pal[0]['ini'], pal[0]['fim'], dur)
        _, b = borda_da_voz(db, voz, pal[-1]['ini'], pal[-1]['fim'], dur)
        return [(max(a, ini - 0.1), min(b, fim + 0.2))], removidas
    bordas = [borda_da_voz(db, voz, p['ini'], p['fim'], dur,
                           pal[k - 1]['fim'] if k > 0 else None,
                           pal[k + 1]['ini'] if k + 1 < len(pal) else None) for k, p in enumerate(pal)]
    # palavras vizinhas não podem se sobrepor por causa da folga
    pedacos = []
    a, b = bordas[0]
    for (s, e) in bordas[1:]:
        if s - b <= JUNTA_SE_GAP:
            b = max(b, e)
        else:
            pedacos.append((a, b))
            a, b = s, e
    pedacos.append((a, b))
    # pedaço curto demais (ex.: uma sílaba solta) gruda no vizinho
    final = []
    for p in pedacos:
        if final and p[1] - p[0] < PEDACO_MINIMO and p[0] - final[-1][1] < 0.35:
            final[-1] = (final[-1][0], p[1])
        elif p[1] - p[0] >= 0.12:
            final.append(p)
    return final, removidas
