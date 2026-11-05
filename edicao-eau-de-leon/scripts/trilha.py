"""
Música de fundo suave — sempre diferente, gerada no próprio computador.

Uso direto (pra ouvir uma amostra):
  python trilha.py saida.wav --duracao 30 [--semente 123]

Cada vídeo ganha uma trilha nova: tom, andamento, sequência de acordes,
instrumentos (piano elétrico, pad, baixo, batida leve) e clima são sorteados.
É "lofi/ambiente" calmo, sem melodia que brigue com a voz. Sem direitos
autorais (é gerada aqui) e sem API paga.

Se houver trilhas licenciadas em assets/musicas, o render usa elas primeiro,
em rodízio (nunca repete a mesma do vídeo anterior). Ver escolher().
"""
import sys as _sys
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

# graus da escala maior (semitons) e progressões calmas (graus 1..7)
MAIOR = [0, 2, 4, 5, 7, 9, 11]
PROGRESSOES = [
    [1, 5, 6, 4], [1, 6, 4, 5], [6, 4, 1, 5], [2, 5, 1, 6], [1, 3, 4, 4],
    [4, 1, 5, 6], [1, 4, 6, 5], [6, 2, 5, 1], [1, 5, 4, 4], [4, 5, 3, 6],
]


def _acorde(raiz_midi, grau):
    """Tétrade diatônica (com 7ª) do grau, em MIDI."""
    i = grau - 1
    notas = []
    for k in (0, 2, 4, 6):
        j = i + k
        notas.append(raiz_midi + MAIOR[j % 7] + 12 * (j // 7))
    return notas


def _hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def _env(n, ataque, queda, sustenta=0.0):
    t = np.arange(n) / SR
    a = np.minimum(1, t / max(ataque, 1e-3))
    d = sustenta + (1 - sustenta) * np.exp(-t / max(queda, 1e-3))
    return a * d


def _passa_baixa(x, corte):
    a = np.exp(-2 * np.pi * corte / SR)
    y = np.empty_like(x)
    acc = 0.0
    b = 1 - a
    for i in range(len(x)):  # um polo; rápido o bastante pra trilha de 60 s
        acc = b * x[i] + a * acc
        y[i] = acc
    return y


def _rhodes(f, n, rnd):
    t = np.arange(n) / SR
    trem = 1 + 0.12 * np.sin(2 * np.pi * rnd.uniform(3.5, 5.5) * t)
    s = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / 0.4) \
        + 0.12 * np.sin(2 * np.pi * 3.01 * f * t) * np.exp(-t / 0.15)
    return s * trem * _env(n, 0.006, 1.6, 0.15)


def _pad(f, n, rnd):
    t = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * f * d * t + rnd.uniform(0, 6.28)) for d in (0.997, 1.0, 1.003))
    s += 0.3 * sum(np.sin(2 * np.pi * 2 * f * d * t) for d in (0.998, 1.002))
    return s * _env(n, 0.9, 99, 1.0) * (1 - np.exp(-(n / SR - t) / 0.6))


def _bumbo(n):
    t = np.arange(n) / SR
    f = 55 + 70 * np.exp(-t / 0.04)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.22)


def _chimbal(n, rnd):
    t = np.arange(n) / SR
    ruido = np.array([rnd.uniform(-1, 1) for _ in range(n)])
    ruido = ruido - _passa_baixa(ruido, 6000)  # só agudo
    return ruido * np.exp(-t / 0.03)


def gerar(duracao, semente=None):
    """Devolve a trilha (estéreo float32, -1..1) com `duracao` segundos."""
    rnd = random.Random(semente)
    bpm = rnd.choice([68, 72, 75, 78, 82, 85, 88])
    tom = rnd.randint(0, 11)
    raiz = 48 + tom  # C3..B3
    prog = rnd.choice(PROGRESSOES)
    com_batida = rnd.random() < 0.7
    com_pad = rnd.random() < 0.8
    com_baixo = rnd.random() < 0.85
    brilho = rnd.uniform(1800, 3200)

    beat = 60 / bpm
    compasso = 4 * beat
    total = int((duracao + 1) * SR)
    L = np.zeros(total)
    R = np.zeros(total)

    def soma(sinal, ini, ganho, pan=0.0):
        i0 = int(ini * SR)
        if i0 >= total:
            return
        s = sinal[: total - i0] * ganho
        L[i0:i0 + len(s)] += s * (1 - pan) * 0.5 * 2 ** 0.5
        R[i0:i0 + len(s)] += s * (1 + pan) * 0.5 * 2 ** 0.5

    c = 0
    t0 = 0.0
    padrao_rhodes = rnd.choice([[0, 2.5], [0, 1.5, 3], [0], [0, 2], [0.5, 2.5]])
    while t0 < duracao + 1:
        notas = _acorde(raiz, prog[c % len(prog)])
        if rnd.random() < 0.3:  # inversão pra variar
            notas = notas[1:] + [notas[0] + 12]
        for p in padrao_rhodes:
            n = int(compasso * SR)
            for k, m in enumerate(notas):
                atraso = k * rnd.uniform(0.008, 0.02)  # "dedilhado" humano
                soma(_rhodes(_hz(m + 12), n, rnd), t0 + p * beat + atraso, 0.10 * rnd.uniform(0.8, 1.0), pan=rnd.uniform(-0.3, 0.3))
        if com_pad:
            n = int(compasso * SR)
            for m in notas[:3]:
                soma(_pad(_hz(m), n, rnd), t0, 0.035)
        if com_baixo:
            n = int(compasso * SR * 0.95)
            soma(_rhodes(_hz(notas[0] - 12), n, rnd), t0, 0.16)
        if com_batida and c >= 1:
            for b in range(4):
                if b in (0, 2) or (b == 3 and rnd.random() < 0.3):
                    soma(_bumbo(int(0.4 * SR)), t0 + b * beat, 0.22)
                for meio in (0, 0.5):
                    if rnd.random() < 0.85:
                        balanço = 0.06 * beat if meio else 0
                        soma(_chimbal(int(0.08 * SR), rnd), t0 + (b + meio) * beat + balanço, 0.035 * rnd.uniform(0.6, 1.0), pan=0.3)
        t0 += compasso
        c += 1

    # ambiente: abafa (lofi), eco curto e um "ar" de vinil bem baixo
    L = _passa_baixa(L, brilho)
    R = _passa_baixa(R, brilho)
    for atraso, ganho in ((0.11, 0.25), (0.23, 0.15), (0.37, 0.08)):
        d = int(atraso * SR)
        L[d:] += ganho * R[:-d]
        R[d:] += ganho * L[:-d]
    chiado = _passa_baixa(np.array([rnd.uniform(-1, 1) for _ in range(total)]), 2500) * 0.004
    L += chiado
    R += chiado
    est = np.stack([L, R], axis=1)[: int(duracao * SR)]
    pico = np.abs(est).max() or 1
    return (est / pico * 0.7).astype(np.float32)


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
    salvar(gerar(duracao + 1, semente), caminho)
    return caminho, f'gerada (semente {semente})'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('saida')
    ap.add_argument('--duracao', type=float, default=30)
    ap.add_argument('--semente', type=int)
    a = ap.parse_args()
    salvar(gerar(a.duracao, a.semente), a.saida)
    print(f'ok: {a.saida}')


if __name__ == '__main__':
    main()
