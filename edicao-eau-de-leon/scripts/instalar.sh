#!/usr/bin/env bash
# Instala o que a skill precisa (Mac/Linux). Rode uma vez: bash scripts/instalar.sh
set -e
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
command -v ffmpeg >/dev/null || { if command -v brew >/dev/null; then brew install ffmpeg; else sudo apt-get install -y ffmpeg; fi; }
command -v python3 >/dev/null || { echo "Instale o Python 3.10+ primeiro"; exit 1; }
python3 -m pip install -r "$RAIZ/requirements.txt"
python3 -c "from faster_whisper import WhisperModel; WhisperModel('small', device='cpu', compute_type='int8'); print('ok')"
python3 "$RAIZ/scripts/verificar.py"
