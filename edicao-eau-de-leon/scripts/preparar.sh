#!/usr/bin/env bash
# Prepara o computador (Mac/Linux) pra skill de edição Eau de Leon.
# O Claude Code roda isto sozinho na primeira edição; pode rodar de novo sem medo.
#   bash scripts/preparar.sh
set -e
AQUI="$(cd "$(dirname "$0")" && pwd)"
RAIZ="$(dirname "$AQUI")"
passo() { printf '\n=== %s ===\n' "$1"; }

passo "1/5 ffmpeg e Python"
if [ "$(uname)" = "Darwin" ]; then
  command -v brew >/dev/null || /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  eval "$(/opt/homebrew/bin/brew shellenv 2>/dev/null || /usr/local/bin/brew shellenv)"
  command -v ffmpeg >/dev/null || brew install ffmpeg
  command -v python3 >/dev/null || brew install python@3.12
else
  if ! command -v ffmpeg >/dev/null || ! command -v python3 >/dev/null; then
    sudo apt-get update && sudo apt-get install -y ffmpeg python3 python3-pip python3-venv
  fi
fi
ffmpeg -hide_banner -filters 2>/dev/null | grep -q " ass " || { echo "FALHA: ffmpeg sem suporte a legenda (libass)"; exit 1; }

passo "2/5 Ambiente Python da skill"
VENV="$RAIZ/.venv"
[ -x "$VENV/bin/python" ] || python3 -m venv "$VENV"
PY="$VENV/bin/python"

passo "3/5 Bibliotecas"
"$PY" -m pip install --upgrade pip -q
"$PY" -m pip install -r "$RAIZ/requirements.txt" -q

passo "4/5 Modelo de transcrição (1ª vez ~500 MB)"
"$PY" -c "from faster_whisper import WhisperModel; WhisperModel('small', device='cpu', compute_type='int8'); print('modelo ok')"

passo "5/5 Conferência"
echo "$PY" > "$AQUI/python.txt"
"$PY" "$AQUI/verificar.py" && printf '\nPRONTO. Use este Python nos comandos da skill:\nPYTHON=%s\n' "$PY"
