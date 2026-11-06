#!/usr/bin/env bash
# Instala (ou atualiza) a skill de edição Eau de Leon no Claude Code — Mac/Linux.
# Baixa a skill E todas as ferramentas (ffmpeg, Python, bibliotecas, modelo).
#   curl -fsSL https://raw.githubusercontent.com/cainaoteiza78-prog/skill-edicao-eau-de-leon/main/instalar-skill.sh | bash
# ou, de dentro do repositório clonado: bash instalar-skill.sh
set -e
DEST="$HOME/.claude/skills/edicao-eau-de-leon"
AQUI="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || echo /nao-existe)"
if [ -f "$AQUI/edicao-eau-de-leon/SKILL.md" ]; then
  ORIGEM="$AQUI/edicao-eau-de-leon"
else
  echo "Baixando a skill do GitHub..."
  TMP="$(mktemp -d)"
  curl -fL -o "$TMP/skill.zip" https://github.com/cainaoteiza78-prog/skill-edicao-eau-de-leon/archive/refs/heads/main.zip
  unzip -q "$TMP/skill.zip" -d "$TMP"
  ORIGEM="$(ls -d "$TMP"/*/ | head -1)edicao-eau-de-leon"
fi
mkdir -p "$HOME/.claude/skills"
GUARDA=""
if [ -d "$DEST/ferramentas" ]; then GUARDA="$HOME/.claude/skills/_ferramentas_eau"; rm -rf "${GUARDA:?}"; mv "$DEST/ferramentas" "$GUARDA"; fi
# atualização: guarda a base de aprendizados DESTA máquina (o que o usuário já ensinou à skill)
APREND=""
if [ -f "$DEST/aprendizados/aprendizados.md" ]; then APREND="$HOME/.claude/skills/_aprendizados_eau.md"; cp -f "$DEST/aprendizados/aprendizados.md" "$APREND"; fi
rm -rf "${DEST:?}"
cp -R "$ORIGEM" "$DEST"
[ -n "$GUARDA" ] && mv "$GUARDA" "$DEST/ferramentas"
if [ -n "$APREND" ]; then mkdir -p "$DEST/aprendizados"; mv -f "$APREND" "$DEST/aprendizados/aprendizados.md"; echo "Aprendizados desta máquina preservados."; fi
echo "Skill copiada para $DEST"
bash "$DEST/scripts/preparar.sh"
