# Validate end-to-end pipeline outputs
# Usage: .\scripts\validate_end_to_end.ps1 -Input outputs/integration_test
# Or: .\scripts\validate_end_to_end.ps1 outputs/integration_test

param(
    [Parameter(Position=0)]
    [string]$OutputDir = "outputs/integration_test"
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

if (Test-Path "venv\Scripts\Activate.ps1") {
    & "venv\Scripts\Activate.ps1"
}

$output = python scripts/validate_end_to_end.py $OutputDir 2>&1
$exitCode = $LASTEXITCODE
Write-Host $output
exit $exitCode
