# Instala a skill no Claude Code (Windows). Rode na pasta do repositório:
#   powershell -ExecutionPolicy Bypass -File .\instalar-skill.ps1
$ErrorActionPreference = 'Stop'
$origem = Join-Path $PSScriptRoot 'edicao-eau-de-leon'
$destino = Join-Path $env:USERPROFILE '.claude\skills\edicao-eau-de-leon'
New-Item -ItemType Directory -Force (Split-Path $destino) | Out-Null
if (Test-Path $destino) { Remove-Item -Recurse -Force $destino }
Copy-Item -Recurse $origem $destino
Write-Host "Skill copiada para $destino"
& powershell -ExecutionPolicy Bypass -File (Join-Path $destino 'scripts\preparar.ps1')
