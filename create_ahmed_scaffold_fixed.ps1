# create_ahmed_scaffold_fixed.ps1
# Clean script to create Ahmed's integration scaffolding and push to feature branch.
# Save as: C:\Users\ec\Documents\Scan\create_ahmed_scaffold_fixed.ps1
# Then run from PowerShell:
#   Set-Location "C:\Users\ec\Documents\Scan"
#   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
#   .\create_ahmed_scaffold_fixed.ps1

$projectPath = "C:\Users\ec\Documents\Scan"

if (!(Test-Path $projectPath)) {
    Write-Error "Project path $projectPath not found. Clone the repo first or create the folder."
    exit 1
}

# Work in project folder
Set-Location $projectPath

# Update main branch to latest
Write-Host "Fetching origin and updating main..."
git fetch origin
git checkout main
git pull origin main

# Create or checkout feature branch
$branchName = "feature/integration-ahmed"
Write-Host "Creating or checking out branch: $branchName"
$exists = git branch --list $branchName
if ($exists) {
    git checkout $branchName
} else {
    git checkout -b $branchName
}

# Ensure directories exist
$dirs = @(
    "src",
    "src\depth",
    "src\detection",
    "src\segmentation",
    "src\scene",
    "src\prompt",
    "src\generation",
    "src\video",
    "docs",
    "scripts",
    ".github\workflows",
    "notebooks",
    "outputs",
    "tests"
)
foreach ($d in $dirs) {
    $full = Join-Path $projectPath $d
    if (!(Test-Path $full)) { New-Item -ItemType Directory -Path $full -Force | Out-Null }
}

# Helper to write files
function Write-File($relativePath, $content) {
    $fullPath = Join-Path $projectPath $relativePath
    $dir = Split-Path $fullPath -Parent
    if (!(Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    Set-Content -Path $fullPath -Value $content -Encoding UTF8
    Write-Host "Wrote $relativePath"
}

# Create src/main.py
$mainPy = @'
#!/usr/bin/env python3
"""
src/main.py

CLI entrypoint for the AI Room Scan pipeline (Ahmed's integration entry).
Usage example:
    python -m src.main --mode image --preset fast --input "samples/input.jpg" --output outputs
"""
import argparse
import logging
import os
from src.config import PRESETS
from src.orchestrator import run_pipeline

def parse_args():
    parser = argparse.ArgumentParser(description="AI Room Scan - orchestration entrypoint")
    parser.add_argument("--mode", choices=["image","video"], required=True, help="image or video input")
    parser.add_argument("--preset", choices=["fast","balanced","quality"], default="fast", help="resource preset")
    parser.add_argument("--input", required=True, help="path to input image, video, or input folder")
    parser.add_argument("--output", default="outputs", help="output directory")
    return parser.parse_args()

def main():
    args = parse_args()
    os.makedirs(args.output, exist_ok=True)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
    logging.info(f"Starting pipeline mode={args.mode} preset={args.preset} input={args.input}")
    run_pipeline(mode=args.mode, preset=args.preset, input_path=args.input, output_dir=args.output)

if __name__ == "__main__":
    main()
'@
Write-File "src\main.py" $mainPy

# Create src/config.py
$configPy = @'
# src/config.py
# Preset mapping and common configuration used by orchestrator
PRESETS = {
    "fast": {
        "midas": "midas_v2_small",
        "yolo": "yolov8n",
        "sam": "sam_box",
        "sd_res": [512,512],
        "sd_steps": 20,
        "guidance": "depth_or_mask"
    },
    "balanced": {
        "midas": "dpt_hybrid",
        "yolo": "yolov8n",
        "sam": "sam_box_prompts",
        "sd_res": [768,768],
        "sd_steps": 25,
        "guidance": "depth_plus_mask_on_keyframes"
    },
    "quality": {
        "midas": "dpt_large",
        "yolo": "yolov8m",
        "sam": "sam_full",
        "sd_res": [1024,1024],
        "sd_steps": 40,
        "guidance": "depth_and_mask"
    }
}
'@
Write-File "src\config.py" $configPy

# Create src/orchestrator.py
$orchestratorPy = @'
# src/orchestrator.py
# High-level pipeline controller (Ahmed)
import os
import json
import logging
from shutil import copyfile

def run_pipeline(mode: str, preset: str, input_path: str, output_dir: str):
    """
    Orchestrator stub. This file provides the integration points and placeholders.
    Replace placeholders with real calls to Batool's and Zohaib's modules once available.
    Expected behavior:
      - call perception modules to produce scene JSON(s)
      - call generation module to create stylized frames
      - assemble video from keyframes
    """
    logging.info("Orchestrator: starting")
    os.makedirs(output_dir, exist_ok=True)

    # 1) Perception step (placeholder)
    scene_dir = os.path.join(output_dir, "scene")
    os.makedirs(scene_dir, exist_ok=True)
    scene_file = os.path.join(scene_dir, "frame_0001.json")
    scene = {
        "frames": [
            {
                "id": "frame_0001",
                "source": os.path.abspath(input_path) if os.path.isfile(input_path) else str(input_path),
                "depth": "depth_frame_0001.png",
                "masks": ["mask_0001_obj1.png"],
                "bboxes": []
            }
        ],
        "preset": preset,
        "mode": mode
    }
    with open(scene_file, "w") as f:
        json.dump(scene, f, indent=2)
    logging.info(f"Saved placeholder scene JSON to: {scene_file}")

    # 2) Generation step (placeholder)
    output_img = os.path.join(output_dir, "frame_0001_styled.png")
    try:
        if os.path.isfile(input_path):
            copyfile(input_path, output_img)
            logging.info(f"Created placeholder styled image at: {output_img}")
        else:
            with open(output_img + ".txt", "w") as f:
                f.write("Placeholder for styled image - provide a real generator to replace this.")
            logging.info(f"Created placeholder marker for styled image at: {output_img}.txt")
    except Exception as e:
        logging.error(f"Error during generation placeholder: {e}")

    # 3) Video assembly (placeholder)
    video_marker = os.path.join(output_dir, "output_video_placeholder.txt")
    with open(video_marker, "w") as f:
        f.write("Video placeholder. Replace with video_maker to assemble keyframes into mp4.")
    logging.info(f"Created video placeholder at: {video_marker}")

    logging.info("Orchestrator: finished (placeholders). Replace placeholders with real modules.")
'@
Write-File "src\orchestrator.py" $orchestratorPy

# Create scripts/run_local.ps1
$runPs1 = @'
param(
    [string]$InputPath = "samples/example.jpg",
    [string]$OutputDir = "outputs"
)
if (Test-Path ".\venv\Scripts\Activate.ps1") {
    . .\venv\Scripts\Activate.ps1
}
python -m src.main --mode image --preset fast --input $InputPath --output $OutputDir
'@
Write-File "scripts\run_local.ps1" $runPs1

# Create docs/README.md
$readmeMd = @'
# AI Room Scan — Project (Ahmed: integration & docs)

## Quick start (Ahmed: CPU-Optimized demo)

1. Clone repo:
   ```powershell
   git clone https://github.com/Ahmedimtiaz-github/Scan.git
   cd Scan
Create virtualenv (recommended):

python -m venv venv
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
Install development/test deps (lightweight):

pip install -r requirements.txt
Run the Fast preset example (placeholder scaffolding):

powershell .\scripts\run_local.ps1 -InputPath "samples/example.jpg" -OutputDir "outputs"
Presets mapping
fast — minimal models & 512×512, 20 steps (default for CPU)

balanced — medium quality & 768×768, 25 steps

quality — high quality & slower (1024×1024, 30–50 steps)

Acceptance criteria (Ahmed)
python -m src.main --mode image --preset fast --input <image> should produce:

outputs/frame_0001_styled.png (placeholder until Zohaib's module is integrated)

outputs/output_video_placeholder.txt
'@
Write-File "docs\README.md" $readmeMd

Create docs/LIMITATIONS.md
$limitMd = @'

LIMITATIONS & DEMO FALLBACKS
CPU-only runs are slow: expect tens of seconds to many minutes per generated image depending on CPU, resolution, and steps.

Recommended baseline for acceptance test: 4 CPU cores + 16 GB RAM.

For high-quality demos, use free cloud resources (Google Colab). Provide Colab instructions in the future.

This repo currently contains integration scaffolding (placeholders). Replace perception and generation placeholders with Batool & Zohaib modules.
'@
Write-File "docs\LIMITATIONS.md" $limitMd

Create requirements.txt
$req = @'
pytest
flake8
'@
Write-File "requirements.txt" $req

Create CI workflow
$ci = @'
name: CI
on:
push:
branches: [ main, feature/* ]
pull_request:
branches: [ main ]
jobs:
tests:
runs-on: ubuntu-latest
steps:
- uses: actions/checkout@v4
- name: Set up Python
uses: actions/setup-python@v4
with:
python-version: 3.10
- name: Install dependencies
run: |
python -m pip install --upgrade pip
pip install -r requirements.txt
- name: Run tests
run: |
pytest -q
'@
Write-File ".github\workflows\ci.yml" $ci

Create notebooks/demo.ipynb
$nb = @'
{
"cells": [
{
"cell_type": "markdown",
"metadata": {},
"source": [
"# Demo notebook (Ahmed)\n",
"\n",
"This notebook will demonstrate an end-to-end Fast preset run once the perception and generation modules are implemented.\n",
"\n",
"Steps to run (when modules are ready):\n",
"1. Install deps and activate venv\n",
"2. Run orchestrator with Fast preset\n",
"3. Display outputs/frame_0001_styled.png\n"
]
}
],
"metadata": {
"kernelspec": {
"display_name": "Python 3",
"language": "python",
"name": "python3"
},
"language_info": {
"name": "python",
"version": "3.10"
}
},
"nbformat": 4,
"nbformat_minor": 5
}
'@
Write-File "notebooks\demo.ipynb" $nb

Root README and .gitignore
Write-File "README.md" "# Scan - AI Room Scan ProjectnThis repo contains the CPU-practical revised project. Ahmed (integration) scaffold added.nSee docs/README.md for Ahmed-specific quickstart and acceptance criteria."
$gitignore = @'
pycache/
.pyc
.env
venv/
outputs/
models/
*.pt
*.pth
*.ckpt
.DS_Store
'@
Write-File ".gitignore" $gitignore

Write-Host "Staging files..."
git add .

Write-Host "Committing..."
try {
git commit -m "Ahmed: add integration scaffolding (main.py, orchestrator, config), docs, CI, notebook" | Out-Null
Write-Host "Commit created."
}
catch {
Write-Host "Commit failed or nothing to commit; continuing."
}

Write-Host "Pushing branch to origin..."
git push -u origin $branchName

Write-Host "Done: Ahmed scaffolding created and pushed to branch $branchName"
