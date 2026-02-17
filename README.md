# AI Room Scan & Interior Styling System (CPU-Optimized Edition)

## Generation & Output Stack

This module provides a complete pipeline for generating stylized interior design images and videos from room scans, optimized specifically for CPU execution.

### Features
- **3 Prompting Modes**: Generic (style-based), Prompt-Based (user input), and Auto-Design (scene analysis).
- **CPU-Optimized Stable Diffusion**: Uses `diffusers` with ControlNet (depth/mask) guidance.
- **Preset Management**: Fast, Balanced, and Quality presets for performance/quality tradeoffs.
- **Video Recomposition**: Creates smooth transitions between styled keyframes.
- **Performance Helpers**: Includes `channels_last` memory format and `torch.compile` support.

### Project Structure
```
ai_room_styling/
├── src/
│   ├── prompt/
│   │   └── prompt_generator.py   # Mode-based prompt logic
│   ├── generation/
│   │   └── sd_runner.py          # SD + ControlNet pipeline
│   ├── video/
│   │   └── video_maker.py        # Video creation from keyframes
│   └── optimizations.py          # CPU optimization helpers
├── tests/
│   └── test_generation.py        # Unit tests
├── scene/
│   └── frame_0001.json           # Sample scene metadata
├── assets/
│   └── room_sample.jpg           # Sample input image
└── outputs/
    └── sample_generation/        # Generated examples
```

### Installation
```bash
pip install diffusers transformers accelerate controlnet_aux opencv-python-headless torch torchvision 
OR
pip install -r requiremwnts.txt
```

### Usage
```python
from src.generation.sd_runner import generate_styled_image

# Generate a styled image
image, path = generate_styled_image(
    scene_json_path="scene/frame_0001.json",
    source_image_path="assets/room_sample.jpg",
    preset="fast",
    mode="auto_design"
)
```

### Unit Tests
Run tests using:
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)
python3 tests/test_generation.py
```
