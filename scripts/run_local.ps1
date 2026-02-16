param(
    [string]$InputPath = "samples/example.jpg",
    [string]$OutputDir = "outputs"
)
if (Test-Path ".\venv\Scripts\Activate.ps1") {
    . .\venv\Scripts\Activate.ps1
}
python -m src.main --mode image --preset fast --input $InputPath --output $OutputDir
