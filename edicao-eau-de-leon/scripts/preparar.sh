#!/usr/bin/env bash
# Prepara TUDO que a skill precisa (Mac/Linux), baixando para dentro da pasta da
# skill (ferramentas/). Não precisa de Python nem ffmpeg instalados antes.
#   bash scripts/preparar.sh
set -e
AQUI="$(cd "$(dirname "$0")" && pwd)"
RAIZ="$(dirname "$AQUI")"
FERR="$RAIZ/ferramentas"; mkdir -p "$FERR/_baixando"; TMP="$FERR/_baixando"
passo() { printf '\n=== %s ===\n' "$1"; }
baixar() { curl -fL --retry 3 -o "$2" "$1"; }
SO="$(uname -s)"; ARQ="$(uname -m)"

passo "1/4 ffmpeg (completo, com legendas)"
if [ ! -x "$FERR/ffmpeg/bin/ffmpeg" ]; then
  mkdir -p "$FERR/ffmpeg/bin"
  if [ "$SO" = "Darwin" ]; then
    baixar "https://evermeet.cx/ffmpeg/getrelease/zip" "$TMP/ffmpeg.zip"
    baixar "https://evermeet.cx/ffmpeg/getrelease/ffprobe/zip" "$TMP/ffprobe.zip"
    unzip -o -q "$TMP/ffmpeg.zip" -d "$FERR/ffmpeg/bin"; unzip -o -q "$TMP/ffprobe.zip" -d "$FERR/ffmpeg/bin"
  else
    A=linux64; [ "$ARQ" = "aarch64" ] && A=linuxarm64
    baixar "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-$A-gpl.tar.xz" "$TMP/ff.tar.xz"
    tar -xf "$TMP/ff.tar.xz" -C "$TMP"; cp "$TMP"/ffmpeg-*/bin/* "$FERR/ffmpeg/bin/"
  fi
  chmod +x "$FERR/ffmpeg/bin/"*
else echo "já baixado"; fi
export PATH="$FERR/ffmpeg/bin:$PATH"

passo "2/4 uv + Python 3.12 (isolados)"
if [ ! -x "$FERR/uv/uv" ]; then
  curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR="$FERR/uv" UV_NO_MODIFY_PATH=1 sh
fi
export UV_PYTHON_INSTALL_DIR="$FERR/python" UV_CACHE_DIR="$FERR/cache-uv"
PY="$FERR/venv/bin/python"
[ -x "$PY" ] || "$FERR/uv/uv" venv "$FERR/venv" --python 3.12 --python-preference only-managed

passo "3/4 Bibliotecas e modelo de transcrição (1ª vez ~1 GB)"
"$FERR/uv/uv" pip install --python "$PY" -r "$RAIZ/requirements.txt"
"$PY" -c "import sys; sys.path.insert(0, '$AQUI'); import ambiente; from huggingface_hub import snapshot_download; snapshot_download('Systran/faster-whisper-small'); print('modelo ok')"

passo "4/4 Conferência"
rm -rf "$TMP"
echo "$PY" > "$AQUI/python.txt"
"$PY" "$AQUI/verificar.py" && printf '\nPRONTO. Use este Python nos comandos da skill:\nPYTHON=%s\n' "$PY"
