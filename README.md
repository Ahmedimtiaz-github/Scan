# AI Room Scan & Interior Styling System (CPU-Optimized Edition)

A CPU-only AI system that takes room images or video, understands layout and objects, and redesigns the room using AI—producing styled images and video.

## Quick start

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

```bash
python -m src.main --mode image --preset fast --input sample_data/sample.jpg --output outputs/integration_test
```

## Presets

| Preset   | Resolution | Steps | Use case        |
|----------|------------|-------|-----------------|
| fast     | 512×512    | 20    | CPU default     |
| balanced | 768×768    | 25    | Better quality  |
| quality  | 1024×1024  | 40    | Best (slow)     |

## Project structure

```
src/
├── main.py              # CLI entrypoint
├── config.py            # Presets (Fast/Balanced/Quality)
├── orchestrator.py      # Pipeline controller
├── input.py             # Video frame extraction
├── adapters/            # Perception & generation adapters
├── depth/               # MiDaS
├── detection/           # YOLOv8
├── segmentation/       # SAM
├── scene/               # Scene builder
├── prompt/              # Prompt generator
├── generation/          # Stable Diffusion + ControlNet
├── video/               # Video assembly
└── optimizations.py     # CPU helpers
```

## Tests

```bash
pytest -q
```

Full integration (requires models):

```bash
RUN_HEAVY=1 pytest -q -v
```

## Documentation

See [docs/README.md](docs/README.md) for setup, run commands, acceptance criteria, and Colab instructions.
