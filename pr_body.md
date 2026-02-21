# Integration: final orchestrator & adapters — Ahmed glue

## Summary of changes

- **Deferred heavy imports**: `main.py` and `orchestrator.py` defer importing torch, diffusers, ultralytics, segment_anything until just before use. CI and lightweight tests run without heavy deps.
- **Robust adapters**:
  - `perception_adapter`: Saves to `out_dir/frames/frame_XXXX/`, returns placeholder frame when heavy libs unavailable.
  - `generation_adapter`: Creates deterministic 512x512 placeholder and `.placeholder` file when model unavailable.
  - `video_adapter`: Added `make_video_from_keyframes(..., crossfade_frames=6)`; writes `video_placeholder.txt` on failure.
- **Validation scripts**: `scripts/validate_end_to_end.py` and `scripts/validate_end_to_end.ps1`.
- **Install scripts**: `scripts/install_heavy_deps_cpu.ps1` and `scripts/install_heavy_deps_cpu.sh`.
- **Colab notebook**: `notebooks/integration_colab.ipynb` for Quality preset demo.
- **CI**: Lightweight `pytest -q`; optional `heavy-demo` job on `workflow_dispatch`.

## How to run

### Windows PowerShell

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt

# Optional: install heavy deps for full pipeline
.\scripts\install_heavy_deps_cpu.ps1

# Run pipeline
python -m src.main --mode image --preset fast --input sample_data/sample.jpg --output outputs/integration_test

# Validate
.\scripts\validate_end_to_end.ps1 -OutputDir outputs/integration_test

# Tests
pytest -q -v --basetemp=./tests/pytest_tmp
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
./scripts/install_heavy_deps_cpu.sh
python -m src.main --mode image --preset fast --input sample_data/sample.jpg --output outputs/integration_test
python scripts/validate_end_to_end.py outputs/integration_test
pytest -q -v --basetemp=./tests/pytest_tmp
```

## Acceptance checklist

- [ ] `pytest -q` passes (lightweight tests)
- [ ] `outputs/integration_test/scene/frame_0001.json` exists and validates against `docs/scene_schema.json`
- [ ] `outputs/integration_test/frame_0001_styled.png` exists and size > 100 bytes
- [ ] `outputs/integration_test/final_video.mp4` or `video_placeholder.txt` exists
- [ ] `scripts/validate_end_to_end.ps1 -OutputDir outputs/integration_test` prints `VALIDATION: PASS`

## Heavy deps install (copy-paste)

```powershell
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install diffusers transformers accelerate safetensors
pip install ultralytics opencv-python-headless pillow jsonschema
pip install git+https://github.com/facebookresearch/segment-anything.git
```

See `README_INSTALL.md` for manual steps and troubleshooting.

## Colab

Open `notebooks/integration_colab.ipynb` in Colab for a Quality preset demo. Run all cells.

## Reviewers

- Batool (perception modules)
- Zohaib (generation modules)

## Label

integration
