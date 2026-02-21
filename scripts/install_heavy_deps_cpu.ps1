# Install heavy ML dependencies for CPU-only runs
# Usage: .\scripts\install_heavy_deps_cpu.ps1

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $projectRoot

$logDir = "logs"
$logFile = "$logDir\install_error.log"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

function Log-Error {
    param([string]$msg)
    Add-Content -Path $logFile -Value "$(Get-Date -Format o) $msg"
    Write-Host "ERROR: $msg" -ForegroundColor Red
}

# Create venv if missing
if (-not (Test-Path "venv")) {
    python -m venv venv
}

& "venv\Scripts\Activate.ps1"

try {
    python -m pip install --upgrade pip
} catch {
    Log-Error "pip upgrade failed: $_"
}

try {
    pip install torch --index-url https://download.pytorch.org/whl/cpu
} catch {
    Log-Error "torch install failed: $_"
}

try {
    pip install diffusers transformers accelerate safetensors
} catch {
    Log-Error "diffusers stack failed: $_"
}

try {
    pip install ultralytics opencv-python-headless pillow jsonschema
} catch {
    Log-Error "ultralytics/opencv failed: $_"
}

try {
    pip install git+https://github.com/facebookresearch/segment-anything.git
} catch {
    Log-Error "segment-anything failed: $_"
    Write-Host "You may need to install segment-anything manually. See README_INSTALL.md"
}

Write-Host "Heavy deps install complete. Check $logFile for any errors."
