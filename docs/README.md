# AI Room Scan & Interior Styling — Documentation

## Setup

### 1. Create virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

On Linux/macOS:

```bash
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Heavy model dependencies (optional for basic runs)

The pipeline uses MiDaS, YOLOv8, SAM, and Stable Diffusion. Install additional deps:

```bash
pip install ultralytics
pip install segment-anything
```

Download SAM checkpoint (`sam_vit_b_01ec64.pth`) and place in project root or set path in SAM runner.

## Running the pipeline

### Image mode (single image)

```bash
python -m src.main --mode image --preset fast --input sample_data/sample.jpg --output outputs/integration_test
```

### Video mode (extract keyframes, style, assemble video)

```bash
python -m src.main --mode video --preset fast --input path/to/video.mp4 --output outputs/video_out --fps 1 --max-frames 10
```

### Presets

| Preset   | Resolution | Steps | MiDaS       | YOLO    | Use case        |
|----------|------------|-------|-------------|---------|-----------------|
| fast     | 512×512    | 20    | MiDaS_small | yolov8n | CPU default     |
| balanced | 768×768    | 25    | DPT_Hybrid  | yolov8n | Better quality  |
| quality  | 1024×1024  | 40    | DPT_Hybrid  | yolov8m | Best (slow)     |

## Integration test

```bash
# Lightweight tests (no model download)
pytest -q

# Full integration (requires models, sample image)
RUN_HEAVY=1 pytest -q -v
```

## Acceptance criteria

- **Fast preset** on baseline hardware (4 cores, 16GB RAM): produce one 512×512 styled image in under ~10–15 minutes (first run includes model download).
- Outputs: `outputs/<run>/scene/frame_0001.json`, `frame_0001_styled.png`, `final_video.mp4`.

## Colab for quality demos

For Quality preset or presentation demos, use Google Colab (free GPU):

1. Upload project to Colab or clone from repo.
2. Install dependencies; optionally enable GPU in Runtime settings.
3. Run:

```python
!python -m src.main --mode image --preset quality --input sample.jpg --output outputs/colab_run
```

## Scene JSON schema

See [docs/scene_schema.json](scene_schema.json) for the schema of scene outputs.
