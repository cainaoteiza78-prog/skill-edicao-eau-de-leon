"""Confere se a máquina está pronta pra skill (ffmpeg com libass, Python libs, fontes, logo, perfumes)."""
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import ambiente  # noqa: F401,E402  (ffmpeg/modelos da pasta da skill)
_sys.stdout.reconfigure(encoding='utf-8', errors='replace')  # console do Windows
import json
import os
import shutil
import subprocess
import sys

RAIZ = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
ok = True


def item(nome, cond, dica=''):
    global ok
    print(f"[{'OK' if cond else 'FALTA'}] {nome}" + ('' if cond else f'  → {dica}'))
    ok &= bool(cond)


item('ffmpeg (da skill ou do PC)', shutil.which('ffmpeg'), 'rode scripts/preparar.ps1 (Windows) ou scripts/preparar.sh')
item('ffprobe no PATH', shutil.which('ffprobe'), 'vem junto com o ffmpeg')
if shutil.which('ffmpeg'):
    filtros = subprocess.run(['ffmpeg', '-hide_banner', '-filters'], capture_output=True, text=True).stdout
    item('ffmpeg com legenda (libass)', ' ass ' in filtros, 'use a build "full" do ffmpeg (gyan.dev no Windows)')
for mod in ('faster_whisper', 'numpy', 'PIL', 'cv2', 'scipy'):
    try:
        __import__(mod)
        item(f'python: {mod}', True)
    except ImportError:
        item(f'python: {mod}', False, 'pip install -r requirements.txt')
for f in ('Poppins-Bold.ttf', 'BebasNeue-Regular.ttf', 'Bungee-Regular.ttf', 'TikTokSans-SemiBold.ttf', 'NotoColorEmoji.ttf'):
    item(f'fonte {f}', os.path.exists(os.path.join(RAIZ, 'assets', 'fontes', f)), 'baixe o repo completo')
import glob as _g
modelo = _g.glob(os.path.join(RAIZ, 'ferramentas', 'modelos', 'hub', 'models--Systran--faster-whisper-small', 'snapshots', '*', 'model.bin'))     or _g.glob(os.path.join(os.path.expanduser('~'), '.cache', 'huggingface', 'hub', 'models--Systran--faster-whisper-small', 'snapshots', '*', 'model.bin'))
item('modelo de transcrição (Whisper small)', modelo, 'rode o preparador de novo (ele baixa o modelo)')
item('logo', os.path.exists(os.path.join(RAIZ, 'assets', 'logo', 'eau-de-leon-branco.png')), 'baixe o repo completo')
pj = os.path.join(RAIZ, 'assets', 'perfumes', 'perfumes.json')
n = len(json.load(open(pj, encoding='utf8'))['perfumes']) if os.path.exists(pj) else 0
item(f'catálogo de perfumes ({n})', n > 0, 'baixe o repo completo (com Git LFS, se usado)')
print('\nTudo pronto.' if ok else '\nCorrija os itens acima.')
sys.exit(0 if ok else 1)
