param(
  [Parameter(Mandatory=$true)][string]$Audio,
  [string]$Output = "output",
  [double]$Bpm = 0
)

$Root = Resolve-Path (Join-Path $PSScriptRoot "../..")
$Python = Join-Path $Root ".venv/Scripts/python.exe"
if (-not (Test-Path $Python)) {
  throw ".venv がありません。先に tools\audio_pipeline\setup_windows.ps1 を実行してください。"
}

$argsList = @("tools/audio_pipeline/pipeline.py", $Audio, "-o", $Output)
if ($Bpm -gt 0) { $argsList += @("--bpm", "$Bpm") }
& $Python @argsList
