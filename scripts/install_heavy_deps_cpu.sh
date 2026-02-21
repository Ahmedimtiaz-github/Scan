#!/bin/bash
# Install heavy ML dependencies for CPU-only runs
# Usage: ./scripts/install_heavy_deps_cpu.sh

set -e
cd "$(dirname "$0")/.."

LOG_DIR="logs"
LOG_FILE="$LOG_DIR/install_error.log"
mkdir -p "$LOG_DIR"

log_error() {
    echo "$(date -Iseconds) $1" >> "$LOG_FILE"
    echo "ERROR: $1" >&2
}

# Create venv if missing
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

python -m pip install --upgrade pip || log_error "pip upgrade failed"
pip install torch --index-url https://download.pytorch.org/whl/cpu || log_error "torch install failed"
pip install diffusers transformers accelerate safetensors || log_error "diffusers stack failed"
pip install ultralytics opencv-python-headless pillow jsonschema || log_error "ultralytics/opencv failed"
pip install git+https://github.com/facebookresearch/segment-anything.git || log_error "segment-anything failed"

echo "Heavy deps install complete. Check $LOG_FILE for any errors."
