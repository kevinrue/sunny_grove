param(
    [string]$PythonPath = (Join-Path $PSScriptRoot "..\.venv\Scripts\python.exe")
)

$ErrorActionPreference = "Stop"
$repositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$python = (Resolve-Path $PythonPath).Path
$distPath = Join-Path $repositoryRoot "dist"
$workPath = Join-Path $repositoryRoot "build\pyinstaller"

if (-not (Test-Path $python -PathType Leaf)) {
    throw "Python interpreter not found: $python"
}

Remove-Item (Join-Path $distPath "Sunny Grove") -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item $workPath -Recurse -Force -ErrorAction SilentlyContinue

Push-Location $repositoryRoot
try {
    & $python -m PyInstaller --noconfirm --clean --distpath $distPath --workpath $workPath packaging\sunny-grove.spec
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller failed with exit code $LASTEXITCODE."
    }
}
finally {
    Pop-Location
}