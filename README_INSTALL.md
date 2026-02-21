# Manual Install Guide (Heavy Dependencies)

If `scripts/install_heavy_deps_cpu.ps1` or `scripts/install_heavy_deps_cpu.sh` fails, use these manual steps.

## CPU PyTorch

```powershell
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

Linux/macOS: same command. See [PyTorch CPU wheels](https://pytorch.org/get-started/locally/) for other options.

## Diffusers stack

```bash
pip install diffusers transformers accelerate safetensors
```

## YOLOv8 and OpenCV

```bash
pip install ultralytics opencv-python-headless pillow jsonschema
```

## Segment Anything (SAM)

```bash
pip install git+https://github.com/facebookresearch/segment-anything.git
```

Or download checkpoint manually:
- [sam_vit_b_01ec64.pth](https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth)
- Place in project root or set path in `src/segmentation/sam_runner.py`

## Troubleshooting

- **torch install fails**: Try `pip install torch --index-url https://download.pytorch.org/whl/cpu` with a specific Python version.
- **segment-anything fails**: Install from GitHub; ensure `git` is available. Alternatively use a prebuilt wheel if available.
- **Out of memory**: Use Fast preset (512x512, 20 steps). Reduce `--max-frames` for video mode.
