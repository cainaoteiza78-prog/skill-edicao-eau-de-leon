# Prepara o computador (Windows) pra skill de edição Eau de Leon.
# O Claude Code roda isto sozinho na primeira edição; pode rodar de novo sem medo
# (o que já estiver instalado é pulado).
#
#   powershell -ExecutionPolicy Bypass -File scripts\preparar.ps1
#
# Instala, se faltar: Python 3.12, ffmpeg (versão completa, com legendas),
# runtime do Visual C++, as bibliotecas Python da skill e o modelo de
# transcrição. Tudo grátis. No fim grava o caminho do Python em scripts\python.txt.
$ErrorActionPreference = 'Continue'
$scripts = $PSScriptRoot
$raiz = Split-Path -Parent $scripts

function Passo($t) { Write-Host "`n=== $t ===" -ForegroundColor Cyan }
function RecarregaPath {
  $env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' + [Environment]::GetEnvironmentVariable('Path', 'User')
}
function TemWinget { [bool](Get-Command winget -ErrorAction SilentlyContinue) }
function Winget($id) {
  if (-not (TemWinget)) { Write-Host "winget nao encontrado. Instale o 'Instalador de Aplicativo' pela Microsoft Store e rode de novo."; exit 1 }
  winget install -e --id $id --silent --accept-package-agreements --accept-source-agreements --disable-interactivity
  RecarregaPath
}
function AchaPython {
  # o "python" da Microsoft Store e um atalho falso: testa de verdade
  $cands = @(
    "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
    "$env:ProgramFiles\Python312\python.exe"
  )
  foreach ($c in @('python', 'py')) {
    $cmd = Get-Command $c -ErrorAction SilentlyContinue
    if ($cmd -and $cmd.Source -notlike '*WindowsApps*') { $cands = @($cmd.Source) + $cands }
  }
  foreach ($c in $cands) {
    if ($c -and (Test-Path $c)) {
      $v = & $c -c "import sys; print(sys.version_info[0]*100+sys.version_info[1])" 2>$null
      if ($v -and [int]$v -ge 310) { return (& $c -c "import sys; print(sys.executable)").Trim() }
    }
  }
  return $null
}

Passo '1/6 Python'
$py = AchaPython
if (-not $py) { Winget 'Python.Python.3.12'; $py = AchaPython }
if (-not $py) { Write-Host 'FALHA: nao consegui instalar o Python. Instale o Python 3.12 em python.org e rode de novo.'; exit 1 }
Write-Host "Python: $py"

Passo '2/6 ffmpeg (com legendas)'
RecarregaPath
$ok = $false
if (Get-Command ffmpeg -ErrorAction SilentlyContinue) {
  $ok = (ffmpeg -hide_banner -filters 2>$null | Select-String ' ass ') -ne $null
}
if (-not $ok) {
  Winget 'Gyan.FFmpeg'
  $ok = (Get-Command ffmpeg -ErrorAction SilentlyContinue) -and ((ffmpeg -hide_banner -filters 2>$null | Select-String ' ass ') -ne $null)
}
if (-not $ok) {
  # winget nao colocou no PATH desta sessao: procura o executavel e adiciona
  $f = Get-ChildItem "$env:LOCALAPPDATA\Microsoft\WinGet" -Recurse -Filter ffmpeg.exe -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($f) {
    $dir = $f.DirectoryName
    $env:Path = "$dir;$env:Path"
    [Environment]::SetEnvironmentVariable('Path', [Environment]::GetEnvironmentVariable('Path', 'User') + ";$dir", 'User')
    $ok = $true
  }
}
if (-not $ok) { Write-Host 'FALHA: ffmpeg nao ficou disponivel. Feche e abra o terminal e rode de novo.'; exit 1 }
Write-Host 'ffmpeg ok'

Passo '3/6 Runtime do Visual C++ (necessario pra transcricao)'
$vc = Test-Path "$env:WINDIR\System32\msvcp140.dll"
if (-not $vc) { Winget 'Microsoft.VCRedist.2015+.x64' } else { Write-Host 'ja instalado' }

Passo '4/6 Bibliotecas Python'
& $py -m pip install --upgrade pip --quiet --disable-pip-version-check
& $py -m pip install -r (Join-Path $raiz 'requirements.txt') --quiet --disable-pip-version-check
if ($LASTEXITCODE -ne 0) { Write-Host 'FALHA no pip install (ver mensagem acima).'; exit 1 }

Passo '5/6 Modelo de transcricao (1a vez baixa ~500 MB)'
& $py -c "from faster_whisper import WhisperModel; WhisperModel('small', device='cpu', compute_type='int8'); print('modelo ok')"

Passo '6/6 Conferencia'
Set-Content -Path (Join-Path $scripts 'python.txt') -Value $py -Encoding ascii
& $py (Join-Path $scripts 'verificar.py')
if ($LASTEXITCODE -eq 0) { Write-Host "`nPRONTO. Use este Python nos comandos da skill:`nPYTHON=$py" -ForegroundColor Green }
exit $LASTEXITCODE
