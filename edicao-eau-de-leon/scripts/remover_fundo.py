"""
Remove o fundo de fotos de perfume e salva PNG com transparência REAL
(canal alfa), recortado rente ao frasco.

Uso:
  python remover_fundo.py <pasta_ou_arquivo_entrada> <pasta_saida> [--modelo birefnet-general]

- Modelo padrão: isnet-general-use (roda local, grátis, ~3 s por foto no CPU).
  Na 1ª vez baixa o modelo (~180 MB) para ~/.rembg/models.
  Em PC com bastante memória dá pra usar --modelo birefnet-general (um pouco
  mais fino nos detalhes, ~25 s por foto e precisa de ~8 GB livres).
- Pula arquivos que já existem na saída (dá pra interromper e retomar).
- Confere cada resultado: os 4 cantos têm de ficar 100% transparentes; se não
  ficarem, o arquivo é listado como SUSPEITO no fim.
"""
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import ambiente  # noqa: F401,E402  (ffmpeg/modelos da pasta da skill)
_sys.stdout.reconfigure(encoding='utf-8', errors='replace')  # console do Windows
import argparse
import os
import sys
import unicodedata
import re

import numpy as np
import onnxruntime as ort
from PIL import Image
from scipy import ndimage
from rembg import new_session, remove

EXT = ('.png', '.jpg', '.jpeg', '.webp')
LADO_MAX = 900  # px no lado maior: nítido em 1080x1920 e leve no repo


def slug(nome: str) -> str:
    s = unicodedata.normalize('NFKD', nome).encode('ascii', 'ignore').decode()
    s = s.lower().replace('&', ' e ').replace('°', '')
    s = re.sub(r'[^a-z0-9]+', '-', s).strip('-')
    return s


def sessao(modelo: str):
    o = ort.SessionOptions()
    # Sem arena de memória: o BiRefNet estoura RAM em PCs com pouca memória virtual.
    o.enable_cpu_mem_arena = False
    o.enable_mem_pattern = False
    o.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_BASIC
    return new_session(modelo, sess_opts=o)


def recortar(im: Image.Image) -> Image.Image:
    alfa = im.getchannel('A')
    # Ignora poeira quase invisível ao medir a caixa do frasco.
    caixa = alfa.point(lambda a: 255 if a > 12 else 0).getbbox()
    if not caixa:
        return im
    l, t, r, b = caixa
    pad = int(max(r - l, b - t) * 0.02)
    im = im.crop((max(0, l - pad), max(0, t - pad), min(im.width, r + pad), min(im.height, b + pad)))
    if max(im.size) > LADO_MAX:
        f = LADO_MAX / max(im.size)
        im = im.resize((round(im.width * f), round(im.height * f)), Image.LANCZOS)
    return im


def reforco_fundo_branco(rgb: Image.Image, alfa: Image.Image, tol: int = 3) -> Image.Image:
    """Foto de catálogo em fundo branco puro: o modelo às vezes "come" partes
    claras do frasco (vidro branco, tampa prateada). Aqui o fundo é o branco
    (255±tol) LIGADO À BORDA; tudo que não é esse fundo e encosta no que o
    modelo achou vira frasco também. Foto sem fundo branco → não mexe."""
    a = np.asarray(rgb).astype(np.int16)
    branco = a.min(axis=2) >= 255 - tol
    borda = np.concatenate([branco[0], branco[-1], branco[:, 0], branco[:, -1]])
    if borda.mean() < 0.9:
        return alfa
    lab, _ = ndimage.label(branco)
    ids = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    frente = ~np.isin(lab, ids[ids > 0])
    modelo = np.asarray(alfa) > 128
    labf, _ = ndimage.label(frente)
    manter = np.unique(labf[modelo & frente])
    frente = np.isin(labf, manter[manter > 0])
    suave = ndimage.gaussian_filter(frente.astype(np.float32), 0.7) * 255
    return Image.fromarray(np.maximum(np.asarray(alfa).astype(np.float32), suave).clip(0, 255).astype(np.uint8))


def cantos_transparentes(im: Image.Image) -> bool:
    a = im.getchannel('A')
    w, h = a.size
    return all(a.getpixel(p) == 0 for p in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('entrada')
    ap.add_argument('saida')
    ap.add_argument('--modelo', default='isnet-general-use')
    ap.add_argument('--refazer', action='store_true', help='sobrescreve o que já existe na saída')
    a = ap.parse_args()

    if os.path.isfile(a.entrada):
        arquivos = [a.entrada]
    else:
        arquivos = [os.path.join(a.entrada, f) for f in sorted(os.listdir(a.entrada)) if f.lower().endswith(EXT)]
    os.makedirs(a.saida, exist_ok=True)
    s = None
    suspeitos = []
    for i, f in enumerate(arquivos, 1):
        destino = os.path.join(a.saida, slug(os.path.splitext(os.path.basename(f))[0]) + '.png')
        if os.path.exists(destino) and not a.refazer:
            continue
        s = s or sessao(a.modelo)
        im = Image.open(f).convert('RGB')
        try:
            mascara = remove(im, session=s).getchannel('A')
        except Exception as e:  # falta de memória momentânea: recria a sessão e tenta de novo
            print(f'  tentando de novo ({type(e).__name__})', flush=True)
            import gc, time
            s = None
            gc.collect()
            time.sleep(3)
            s = sessao(a.modelo)
            mascara = remove(im, session=s).getchannel('A')
        alfa = reforco_fundo_branco(im, mascara)
        out = im.convert('RGBA')
        out.putalpha(alfa)
        out = recortar(out)
        # Garante 0 absoluto no fundo (sem "fundo fantasma" de 1-3% de opacidade).
        r, g, b, al = out.split()
        al = al.point(lambda v: 0 if v < 8 else v)
        out = Image.merge('RGBA', (r, g, b, al))
        out.save(destino, optimize=True)
        if not cantos_transparentes(out):
            suspeitos.append(destino)
        print(f'[{i}/{len(arquivos)}] {os.path.basename(destino)}', flush=True)
    if suspeitos:
        print('SUSPEITOS (conferir à mão):', *suspeitos, sep='\n  ')


if __name__ == '__main__':
    sys.exit(main())
