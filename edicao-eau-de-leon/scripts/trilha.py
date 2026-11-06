"""
Música de fundo ANIMADA — sempre diferente, gerada no próprio computador.

Uso direto (pra ouvir uma amostra):
  python trilha.py saida.wav --duracao 30 [--semente 123] [--clima pop|funk|house|tropical]

Cada vídeo ganha uma trilha nova, alegre e dinâmica (sensação divertida), mas
sem melodia cantável que roube a cena da fala: tom maior, 104–124 bpm, batida
com bumbo + palma + chimbal, baixo sincopado, acordes em contratempo e um
arpejo brilhante (marimba/pluck). Clima, tom, andamento, acordes, timbres e
partes (entra/sai instrumento a cada 4 compassos) são sorteados.

Sem direitos autorais (é gerada aqui) e sem API paga. Se houver trilhas
licenciadas em assets/musicas, o render usa elas primeiro, em rodízio.
"""
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import ambiente  # noqa: F401,E402  (ffmpeg/modelos da pasta da skill)
_sys.stdout.reconfigure(encoding='utf-8', errors='replace')  # console do Windows
import argparse
import json
import os
import random
import wave

import numpy as np

SR = 44100
AQUI = os.path.dirname(os.path.abspath(__file__))
MUSICAS = os.path.normpath(os.path.join(AQUI, '..', 'assets', 'musicas'))
ESTADO = os.path.join(MUSICAS, '.rodizio.json')

MAIOR = [0, 2, 4, 5, 7, 9, 11]
PROGRESSOES = [[1, 5, 6, 4], [4, 5, 3, 6], [1, 4, 5, 4], [6, 4, 1, 5], [1, 6, 4, 5], [2, 5, 1, 1], [4, 1, 5, 6], [1, 3, 4, 5]]
CLIMAS = {
    #          bpm            bumbo no "e do 2"  balanço  brilho(Hz)    arpejo
    'pop':      ((112, 124), 0.5, 0.00, (7000, 9000), 'pluck'),
    'funk':     ((104, 114), 0.8, 0.10, (5500, 7500), 'marimba'),
    'house':    ((118, 124), 0.0, 0.00, (6500, 9000), 'pluck'),
    'tropical': ((104, 112), 0.6, 0.06, (6000, 8000), 'marimba'),
}


def _hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def _acorde(raiz, grau):
    i = grau - 1
    return [raiz + MAIOR[(i + k) % 7] + 12 * ((i + k) // 7) for k in (0, 2, 4, 6)]


def _t(n):
    return np.arange(n) / SR


def _passa_baixa(x, corte):
    """Filtro de 1 polo, vetorizado em blocos (rápido)."""
    from scipy.signal import lfilter
    a = np.exp(-2 * np.pi * corte / SR)
    return lfilter([1 - a], [1, -a], x)


def _passa_alta(x, corte):
    return x - _passa_baixa(x, corte)


def pluck(f, dur):
    n = int(dur * SR)
    t = _t(n)
    s = (np.sign(np.sin(2 * np.pi * f * t)) * 0.35 + np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t))
    return s * np.exp(-t / 0.16) * np.minimum(1, t / 0.003)


def marimba(f, dur):
    n = int(dur * SR)
    t = _t(n)
    s = np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * 4 * f * t) * np.exp(-t / 0.03)
    return s * np.exp(-t / 0.22) * np.minimum(1, t / 0.002)


def stab(freqs, dur):
    n = int(dur * SR)
    t = _t(n)
    s = sum(np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * 2 * f * t) + 0.15 * np.sin(2 * np.pi * 3 * f * t) for f in freqs)
    return s / len(freqs) * np.exp(-t / 0.12) * np.minimum(1, t / 0.004)


def baixo(f, dur):
    n = int(dur * SR)
    t = _t(n)
    s = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t)
    return np.tanh(1.6 * s) * np.exp(-t / 0.35) * np.minimum(1, t / 0.004)


def bumbo(rs):
    n = int(0.35 * SR)
    t = _t(n)
    f = 48 + 95 * np.exp(-t / 0.035)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.2) + 0.15 * rs.uniform(-1, 1, n) * np.exp(-t / 0.004)


def palma(rs):
    n = int(0.25 * SR)
    t = _t(n)
    r = _passa_alta(rs.uniform(-1, 1, n), 1200)
    env = sum(np.exp(-np.maximum(0, t - d) / 0.012) * (t >= d) for d in (0, 0.011, 0.022)) + 0.6 * np.exp(-t / 0.09)
    return r * env * 0.6


def chimbal(rs, aberto=False):
    n = int((0.22 if aberto else 0.06) * SR)
    t = _t(n)
    return _passa_alta(rs.uniform(-1, 1, n), 7000) * np.exp(-t / (0.08 if aberto else 0.018))


def gerar(duracao, semente=None, clima=None):
    """Trilha estéreo float32 (-1..1) com `duracao` segundos."""
    rnd = random.Random(semente)
    rs = np.random.RandomState(rnd.randint(0, 2 ** 31 - 1))
    clima = clima or rnd.choice(list(CLIMAS))
    (b0, b1), p_e2, balanco, (br0, br1), timbre_arp = CLIMAS[clima]
    bpm = rnd.randint(b0, b1)
    raiz = 48 + rnd.randint(0, 11)
    prog = rnd.choice(PROGRESSOES)
    beat = 60 / bpm
    semi = beat / 2
    total = int((duracao + 1.5) * SR)
    L, R = np.zeros(total), np.zeros(total)

    def soma(s, ini, ganho, pan=0.0):
        i0 = int(ini * SR)
        if i0 >= total or i0 < 0:
            return
        s = s[: total - i0] * ganho
        L[i0:i0 + len(s)] += s * (1 - pan)
        R[i0:i0 + len(s)] += s * (1 + pan)

    arp_f = pluck if timbre_arp == 'pluck' else marimba
    padrao_arp = rnd.choice([[0, 1, 2, 1, 3, 2, 1, 2], [0, 2, 1, 3, 2, 1, 3, 2], [0, 1, 2, 3, 2, 1, 0, 2], [3, 2, 1, 0, 1, 2, 3, 1]])
    padrao_baixo = rnd.choice([[0, None, 0, 12, None, 0, 12, None], [0, None, None, 0, None, 0, 7, 12], [0, 0, None, 12, 0, None, 12, 0]])
    compasso = 4 * beat
    c, t0 = 0, 0.0
    while t0 < duracao + 1:
        parte = (c // 4) % 4                     # muda a cada 4 compassos
        notas = _acorde(raiz, prog[c % len(prog)])
        com_arp = parte != 0 or c >= 2
        com_bateria = c >= 1
        cheio = parte in (1, 3)
        for k in range(8):                       # colcheias
            tk = t0 + k * semi + (balanco * semi if k % 2 else 0)
            if com_arp:
                m = notas[padrao_arp[k]] + 24
                soma(arp_f(_hz(m), 0.4), tk, 0.11 * rnd.uniform(0.75, 1.0), pan=0.35 if k % 2 else -0.35)
            pb = padrao_baixo[k]
            if pb is not None:
                soma(baixo(_hz(notas[0] - 12 + pb), semi * 0.95), tk, 0.30)
            if com_bateria:
                soma(chimbal(rs, aberto=(k % 2 == 1 and cheio and rnd.random() < 0.35)), tk, 0.10 if k % 2 else 0.06, pan=0.25)
        if com_bateria:
            for b in range(4):
                if clima == 'house' or b in (0, 2):
                    soma(bumbo(rs), t0 + b * beat, 0.55)
                if b in (1, 3):
                    soma(palma(rs), t0 + b * beat, 0.32 if cheio else 0.26)
            if rnd.random() < p_e2:
                soma(bumbo(rs), t0 + 1.5 * beat, 0.40)
        for off in (0.5, 1.5, 2.5, 3.5):         # acordes no contratempo
            if parte != 2 or off in (1.5, 3.5):
                soma(stab([_hz(x + 12) for x in notas[:3]], semi * 0.9), t0 + off * beat, 0.10, pan=rnd.uniform(-0.2, 0.2))
        if c % 4 == 3 and com_bateria:            # virada no fim de cada parte
            for k in range(4):
                soma(palma(rs), t0 + 3 * beat + k * beat / 4, 0.12 + 0.04 * k)
        t0 += compasso
        c += 1

    brilho = rnd.uniform(br0, br1)
    L, R = _passa_baixa(L, brilho), _passa_baixa(R, brilho)
    d = int(beat * 0.75 * SR)                    # eco rítmico leve
    L[d:] += 0.12 * R[:-d]
    R[d:] += 0.12 * L[:-d]
    est = np.stack([L, R], axis=1)[: int(duracao * SR)]
    est = np.tanh(est / (np.percentile(np.abs(est), 99.5) or 1) * 0.9)   # compressão suave
    return (est / (np.abs(est).max() or 1) * 0.8).astype(np.float32), {'clima': clima, 'bpm': bpm}


def salvar(arr, caminho):
    pcm = (np.clip(arr, -1, 1) * 32767).astype(np.int16)
    with wave.open(caminho, 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def escolher(duracao, pasta_trabalho):
    """Trilha pro vídeo: licenciada em rodízio (se houver) ou uma nova gerada."""
    cand = sorted(f for f in os.listdir(MUSICAS) if f.lower().endswith(('.mp3', '.wav', '.m4a'))) \
        if os.path.isdir(MUSICAS) else []
    if cand:
        try:
            usadas = json.load(open(ESTADO, encoding='utf8'))
        except (OSError, ValueError):
            usadas = []
        livres = [f for f in cand if f not in usadas] or cand
        esc = random.choice(livres)
        usadas = (usadas + [esc])[-max(1, len(cand) - 1):]
        try:
            json.dump(usadas, open(ESTADO, 'w', encoding='utf8'))
        except OSError:
            pass
        return os.path.join(MUSICAS, esc), f'licenciada: {esc}'
    semente = random.SystemRandom().randint(0, 10 ** 9)
    caminho = os.path.join(pasta_trabalho, 'trilha.wav')
    arr, info = gerar(duracao + 1, semente)
    salvar(arr, caminho)
    return caminho, f"gerada: {info['clima']}, {info['bpm']} bpm (semente {semente})"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('saida')
    ap.add_argument('--duracao', type=float, default=30)
    ap.add_argument('--semente', type=int)
    ap.add_argument('--clima', choices=list(CLIMAS))
    a = ap.parse_args()
    arr, info = gerar(a.duracao, a.semente, a.clima)
    salvar(arr, a.saida)
    print(f"ok: {a.saida} ({info['clima']}, {info['bpm']} bpm)")


if __name__ == '__main__':
    main()
