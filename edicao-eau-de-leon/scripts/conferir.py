"""
Passo 4: tira quadros do vídeo editado e monta folhas de contato (PNG) pra
conferir com os olhos (o Claude abre o PNG com a ferramenta Read).

Uso:
  python conferir.py <video.mp4> [--cada 1.0] [--em 0.5,2.3,7.1] [--saida pasta]

Sem --em: um quadro a cada --cada segundos + os instantes de texto/perfume/b-roll
da linha_do_tempo.json (se existir ao lado do vídeo). Gera conferir_01.png,
conferir_02.png... com 8 quadros cada, tempo escrito em amarelo.
"""
import sys as _sys
_sys.stdout.reconfigure(encoding='utf-8', errors='replace')  # console do Windows
import argparse
import json
import os
import subprocess

from PIL import Image, ImageDraw


def quadro(video, t, destino):
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', f'{t:.3f}', '-i', video, '-frames:v', '1', '-vf', 'scale=270:480', destino], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('video')
    ap.add_argument('--cada', type=float, default=1.0)
    ap.add_argument('--em', default='')
    ap.add_argument('--saida', default='')
    a = ap.parse_args()
    video = os.path.abspath(a.video)
    pasta = a.saida or os.path.join(os.path.dirname(video), 'conferir')
    os.makedirs(pasta, exist_ok=True)
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', video],
                               capture_output=True, text=True).stdout)
    if a.em:
        tempos = [float(x) for x in a.em.split(',')]
    else:
        tempos = [round(x * a.cada, 2) for x in range(int(dur / a.cada) + 1)]
        lt = os.path.join(os.path.dirname(video), 'linha_do_tempo.json')
        if os.path.exists(lt):
            r = json.load(open(lt, encoding='utf8'))
            for k in ('textos', 'perfumes', 'broll'):
                for e in r.get(k, []):
                    tempos += [e['ini'] + 0.5]
        tempos = sorted({min(max(0, t), dur - 0.05) for t in tempos})
    folhas = []
    for f0 in range(0, len(tempos), 8):
        bloco = tempos[f0:f0 + 8]
        folha = Image.new('RGB', (270 * len(bloco), 505), (0, 0, 0))
        d = ImageDraw.Draw(folha)
        for i, t in enumerate(bloco):
            q = os.path.join(pasta, '_q.png')
            quadro(video, t, q)
            folha.paste(Image.open(q), (i * 270, 25))
            d.text((i * 270 + 6, 5), f'{t:.2f}s', fill=(255, 230, 0))
        nome = os.path.join(pasta, f'conferir_{len(folhas) + 1:02d}.png')
        folha.save(nome)
        folhas.append(nome)
    os.remove(os.path.join(pasta, '_q.png'))
    print('\n'.join(folhas))


if __name__ == '__main__':
    main()
