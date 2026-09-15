param(
  [switch]$Minimal
)

$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "../..")
Set-Location $Root

if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
  throw "Python Launcher (py) が見つかりません。Python 3.11 を先にインストールしてください。"
}

if (-not (Test-Path ".venv")) {
  py -3.11 -m venv .venv
}

$Python = Join-Path $Root ".venv/Scripts/python.exe"
& $Python -m pip install --upgrade pip
& $Python -m pip install -r tools/audio_pipeline/requirements.txt

if (-not $Minimal) {
  Write-Host "Demucs と drumsep を追加します..."
  & $Python -m pip install demucs drumsep
}

Write-Host ""
Write-Host "セットアップ完了"
Write-Host "実行例:"
Write-Host ".venv\Scripts\python.exe tools\audio_pipeline\pipeline.py C:\path\song.wav -o output"
