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
    'comecar', 'começar', 'comeco', 'começo', 'desde', 'o', 'do', 'pode', 'ir', 'posso', 'ja', 'já',
}
# Pelo menos uma destas tem que estar no trecho isolado pra ele ser bastidor
# (evita apagar um "e aí" ou "então" que é parte da fala).
FORTES = {'corta', 'corte', 'cortar', 'cortou', 'vai', 'parou', 'pera', 'perai', 'espera', 'novo', 'denovo',
          'repete', 'repetir', 'repetindo', 'errei', 'gravando', 'grava', 'gravou', 'valendo', 'acao',
          'ok', 'okay', 'bora', 'droga', 'again', 'calma', 'hum', 'hm', 'uh', 'eh', 'ah', 'vez', 'pode', 'posso'}
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


SILENCIO_DB = 32     # abaixo de (voz - 32 dB) é silêncio de verdade (não é consoante)
SILENCIO_MIN = 0.16  # silêncio dentro do tempo de uma palavra só sai se for maior que isso
RESPIRO_DB = 20      # entre palavras: abaixo de (voz - 20 dB) é respiração/pausa → sai


def pedacos_do_trecho(palavras_take, db, voz, ini, fim, dur, manter_pausas=False):
    """[(a,b), ...] dentro de [ini,fim] da take: só fala, sem bastidor, respiração ou pausa.

    REGRA QUE NÃO PODE QUEBRAR: nenhuma palavra mantida é cortada. O tempo de cada
    palavra (Whisper) é protegido; dele só sai silêncio de verdade (> 0,16 s abaixo
    de voz-32 dB, ex.: o Whisper esticou a palavra por cima de uma pausa). O que é
    cortado fica ENTRE palavras. As bordas ainda crescem pra pegar consoante que o
    Whisper deixou de fora (o "s" final, o "t" inicial).
    """
    n = len(db)
    pal = [p for p in palavras_take if ini - 0.05 <= (p['ini'] + p['fim']) / 2 <= fim + 0.05]
    if not pal:
        return [(ini, fim)], []
    pal, removidas = tirar_bastidor(pal, ini, fim)
    if not pal:
        return [], removidas
    fr = lambda s: max(0, min(n, int(round(s / PASSO))))
    # silêncio = perto do ruído de fundo DESTA take (sala, ar-condicionado),
    # nunca acima de voz-20 dB (aí já pode ser consoante)
    piso = float(np.percentile(db, 10))
    silencio = db < min(voz - RESPIRO_DB, max(voz - SILENCIO_DB, piso + 8))
    fraco = db < voz - RESPIRO_DB

    def ilhas(a, b):
        """Partes de [a,b] com som (tira silêncios internos longos)."""
        out, ini_s, k = [], a, fr(a)
        while k < fr(b):
            if silencio[k]:
                j = k
                while j < fr(b) and silencio[j]:
                    j += 1
                if (j - k) * PASSO >= SILENCIO_MIN:
                    if k * PASSO - ini_s > 0.02:
                        out.append((ini_s, k * PASSO))
                    ini_s = j * PASSO
                k = j
            else:
                k += 1
        if b - ini_s > 0.02:
            out.append((ini_s, b))
        return out or [(a, b)]

    blocos = []
    for k, p in enumerate(pal):
        a, b = p['ini'], p['fim']
        esq = pal[k - 1]['fim'] if k else max(0.0, a - 0.30)
        dirt = pal[k + 1]['ini'] if k + 1 < len(pal) else min(dur, b + 0.40)
        # cresce enquanto ainda é som (consoante/fim de sílaba), sem invadir a vizinha
        while fr(a) - 1 >= fr(esq) and fr(a) - 1 >= 0 and not fraco[fr(a) - 1] and p['ini'] - a < 0.15:
            a -= PASSO
        while fr(b) < fr(dirt) and fr(b) < n and not fraco[fr(b)] and b - p['fim'] < 0.25:
            b += PASSO
        for x, y in ilhas(a, b):
            blocos.append([max(0.0, x - FOLGA_INICIO), min(dur, y + FOLGA_FIM)])
    blocos.sort()
    # junta o que encosta; o que separa é pausa/respiração entre palavras
    junt = [blocos[0]]
    for x, y in blocos[1:]:
        if manter_pausas or x - junt[-1][1] <= JUNTA_SE_GAP:
            junt[-1][1] = max(junt[-1][1], y)
        else:
            junt.append([x, y])
    # garantia final: toda palavra mantida cabe inteira dentro de algum pedaço
    # (a parte COM SOM da palavra; silêncio que o Whisper grudou nela pode sair)
    for p in pal:
        som = [k for k in range(fr(p['ini']), max(fr(p['ini']) + 1, fr(p['fim']))) if k < n and not silencio[k]]
        if not som:
            continue
        s_ini, s_fim = som[0] * PASSO, (som[-1] + 1) * PASSO
        if any(x <= s_ini and s_fim <= y for x, y in junt):
            continue
        cobre = [q for q in junt if q[1] > s_ini and q[0] < s_fim]
        if cobre:
            novo = [min(cobre[0][0], s_ini - FOLGA_INICIO), max(cobre[-1][1], s_fim + FOLGA_FIM)]
            junt = [q for q in junt if q not in cobre] + [novo]
        else:
            junt.append([s_ini - FOLGA_INICIO, s_fim + FOLGA_FIM])
        junt.sort()
    final = []
    for x, y in junt:
        if final and x <= final[-1][1] + JUNTA_SE_GAP:
            final[-1][1] = max(final[-1][1], y)
        else:
            final.append([x, y])
    return [(max(0.0, x), min(dur, y)) for x, y in final], removidas
