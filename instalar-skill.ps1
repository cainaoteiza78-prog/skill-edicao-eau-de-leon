# Instala (ou atualiza) a skill de edicao Eau de Leon no Claude Code - Windows.
# Baixa a skill E todas as ferramentas (ffmpeg, Python, bibliotecas, modelo).
#
# Jeito mais facil (nao precisa de git), no PowerShell:
#   irm https://raw.githubusercontent.com/cainaoteiza78-prog/skill-edicao-eau-de-leon/main/instalar-skill.ps1 | iex
# Ou, de dentro do repositorio clonado:
#   powershell -ExecutionPolicy Bypass -File .\instalar-skill.ps1
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$destino = Join-Path $env:USERPROFILE '.claude\skills\edicao-eau-de-leon'

$origem = $null
if ($PSScriptRoot -and (Test-Path (Join-Path $PSScriptRoot 'edicao-eau-de-leon\SKILL.md'))) {
  $origem = Join-Path $PSScriptRoot 'edicao-eau-de-leon'
} else {
  Write-Host 'Baixando a skill do GitHub...'
  $tmp = Join-Path $env:TEMP ('skill-eau-' + [guid]::NewGuid())
  New-Item -ItemType Directory -Force $tmp | Out-Null
  $zip = Join-Path $tmp 'skill.zip'
  Invoke-WebRequest 'https://github.com/cainaoteiza78-prog/skill-edicao-eau-de-leon/archive/refs/heads/main.zip' -OutFile $zip -UseBasicParsing
  Expand-Archive $zip -DestinationPath $tmp -Force
  $origem = Join-Path (Get-ChildItem $tmp -Directory | Select-Object -First 1).FullName 'edicao-eau-de-leon'
}

New-Item -ItemType Directory -Force (Split-Path $destino) | Out-Null
# atualizacao: guarda as ferramentas ja baixadas (ffmpeg, Python, modelos ~1 GB)
$guarda = $null
if (Test-Path (Join-Path $destino 'ferramentas')) {
  $guarda = Join-Path (Split-Path $destino) '_ferramentas_eau'
  if (Test-Path $guarda) { Remove-Item -Recurse -Force $guarda }
  Move-Item (Join-Path $destino 'ferramentas') $guarda
}
if (Test-Path $destino) { Remove-Item -Recurse -Force $destino }
Copy-Item -Recurse $origem $destino
if ($guarda) { Move-Item $guarda (Join-Path $destino 'ferramentas') }
Write-Host "Skill copiada para $destino"
& powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $destino 'scripts\preparar.ps1')
