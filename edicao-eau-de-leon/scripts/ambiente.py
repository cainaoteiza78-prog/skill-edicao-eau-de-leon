"""Faz os scripts usarem as ferramentas que o instalador baixou para dentro da
skill (ferramentas/ffmpeg/bin), sem depender do que está instalado no PC."""
import os
import sys

_RAIZ = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
_BIN = os.path.join(_RAIZ, 'ferramentas', 'ffmpeg', 'bin')
if os.path.isdir(_BIN) and _BIN not in os.environ.get('PATH', ''):
    os.environ['PATH'] = _BIN + os.pathsep + os.environ.get('PATH', '')
# modelos de transcrição/remoção de fundo também ficam dentro da skill
os.environ.setdefault('HF_HOME', os.path.join(_RAIZ, 'ferramentas', 'modelos'))
os.environ.setdefault('U2NET_HOME', os.path.join(_RAIZ, 'ferramentas', 'modelos', 'rembg'))
os.environ.setdefault('HF_HUB_DISABLE_SYMLINKS_WARNING', '1')
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
