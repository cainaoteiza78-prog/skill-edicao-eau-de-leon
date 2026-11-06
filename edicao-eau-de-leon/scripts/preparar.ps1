# Prepara TUDO que a skill precisa, baixando para dentro da propria pasta da skill
# (ferramentas\). Nao precisa de Python, ffmpeg nem winget instalados antes, nem
# de permissao de administrador. Pode rodar de novo: o que ja existe e pulado.
#
#   powershell -ExecutionPolicy Bypass -File scripts\preparar.ps1
#
# Baixa: ffmpeg completo (com legendas), uv + Python 3.12 isolado, bibliotecas
# (requirements.txt) e o modelo de transcricao. Tudo gratis.
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$scripts = $PSScriptRoot
$raiz = Split-Path -Parent $scripts
$ferr = Join-Path $raiz 'ferramentas'
New-Item -ItemType Directory -Force $ferr | Out-Null
$tmp = Join-Path $ferr '_baixando'
New-Item -ItemType Directory -Force $tmp | Out-Null

function Passo($t) { Write-Host "`n=== $t ===" -ForegroundColor Cyan }
function Baixar($url, $destino) {
  for ($i = 1; $i -le 3; $i++) {
    try { Invoke-WebRequest -Uri $url -OutFile $destino -UseBasicParsing; return }
    catch { Write-Host "  tentativa $i falhou: $($_.Exception.Message)"; Start-Sleep -Seconds 3 }
  }
  throw "Nao consegui baixar $url (verifique a internet e rode de novo)."
}

Passo '1/5 ffmpeg (versao completa, com legendas)'
$ffbin = Join-Path $ferr 'ffmpeg\bin'
if (-not (Test-Path (Join-Path $ffbin 'ffmpeg.exe'))) {
  $zip = Join-Path $tmp 'ffmpeg.zip'
  Baixar 'https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip' $zip
  Expand-Archive -Path $zip -DestinationPath $tmp -Force
  $pasta = Get-ChildItem $tmp -Directory | Where-Object { $_.Name -like 'ffmpeg-*' } | Select-Object -First 1
  New-Item -ItemType Directory -Force (Join-Path $ferr 'ffmpeg') | Out-Null
  Copy-Item -Recurse -Force (Join-Path $pasta.FullName 'bin') (Join-Path $ferr 'ffmpeg')
} else { Write-Host 'ja baixado' }
$env:Path = "$ffbin;$env:Path"

Passo '2/5 uv + Python 3.12 (isolados, dentro da skill)'
$uv = Join-Path $ferr 'uv\uv.exe'
if (-not (Test-Path $uv)) {
  $zip = Join-Path $tmp 'uv.zip'
  Baixar 'https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-pc-windows-msvc.zip' $zip
  Expand-Archive -Path $zip -DestinationPath (Join-Path $ferr 'uv') -Force
} else { Write-Host 'uv ja baixado' }
$env:UV_PYTHON_INSTALL_DIR = Join-Path $ferr 'python'
$env:UV_CACHE_DIR = Join-Path $ferr 'cache-uv'
$venv = Join-Path $ferr 'venv'
$py = Join-Path $venv 'Scripts\python.exe'
if (-not (Test-Path $py)) { & $uv venv $venv --python 3.12 --python-preference only-managed; if ($LASTEXITCODE) { throw 'falha ao criar o Python' } }
else { Write-Host 'Python ja pronto' }

Passo '3/5 Runtime do Visual C++ (transcricao)'
if (-not (Test-Path "$env:WINDIR\System32\msvcp140.dll")) {
  $vc = Join-Path $tmp 'vc_redist.x64.exe'
  Baixar 'https://aka.ms/vs/17/release/vc_redist.x64.exe' $vc
  Start-Process $vc -ArgumentList '/install', '/quiet', '/norestart' -Wait
} else { Write-Host 'ja instalado' }

Passo '4/5 Bibliotecas e modelo de transcricao (1a vez ~1 GB)'
& $uv pip install --python $py -r (Join-Path $raiz 'requirements.txt')
if ($LASTEXITCODE) { throw 'falha ao instalar as bibliotecas' }
& $py -c "import sys; sys.path.insert(0, r'$scripts'); import ambiente; from huggingface_hub import snapshot_download; snapshot_download('Systran/faster-whisper-small'); print('modelo ok')"
if ($LASTEXITCODE) { throw 'falha ao baixar o modelo de transcricao (rode de novo)' }

Passo '5/5 Conferencia'
Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
Set-Content -Path (Join-Path $scripts 'python.txt') -Value $py -Encoding ascii
& $py (Join-Path $scripts 'verificar.py')
if ($LASTEXITCODE -eq 0) { Write-Host "`nPRONTO. Use este Python nos comandos da skill:`nPYTHON=$py" -ForegroundColor Green }
exit $LASTEXITCODE
