# Instala o que a skill precisa (Windows). Rode uma vez:
#   powershell -ExecutionPolicy Bypass -File scripts\instalar.ps1
$ErrorActionPreference = 'Stop'
$raiz = Split-Path -Parent $PSScriptRoot

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
  Write-Host 'Instalando Python 3.12...'
  winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
  Write-Host 'Feche e abra o terminal e rode este script de novo.'; exit 1
}
if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
  Write-Host 'Instalando ffmpeg...'
  winget install -e --id Gyan.FFmpeg --accept-package-agreements --accept-source-agreements
  Write-Host 'Feche e abra o terminal e rode este script de novo.'; exit 1
}
python -m pip install --upgrade pip
python -m pip install -r (Join-Path $raiz 'requirements.txt')
Write-Host 'Baixando o modelo de transcricao (1a vez, ~500 MB)...'
python -c "from faster_whisper import WhisperModel; WhisperModel('small', device='cpu', compute_type='int8'); print('ok')"
python (Join-Path $PSScriptRoot 'verificar.py')
