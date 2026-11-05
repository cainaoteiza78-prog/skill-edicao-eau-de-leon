#!/usr/bin/env bash
# Instala a skill no Claude Code (Mac/Linux). Rode na pasta do repositório: bash instalar-skill.sh
set -e
AQUI="$(cd "$(dirname "$0")" && pwd)"
DEST="$HOME/.claude/skills/edicao-eau-de-leon"
mkdir -p "$HOME/.claude/skills"
rm -rf "${DEST:?}"
cp -R "$AQUI/edicao-eau-de-leon" "$DEST"
echo "Skill copiada para $DEST"
bash "$DEST/scripts/preparar.sh"
