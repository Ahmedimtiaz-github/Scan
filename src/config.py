"""
Presets and model selection logic for Fast/Balanced/Quality modes.
CPU-optimized defaults per Scan Revised spec.
"""

from typing import Any

PRESETS = {
    "fast": {
        "midas_model": "MiDaS_small",
        "yolo_model": "yolov8n.pt",
        "sam_mode": "box-only",
        "sd_resolution": (512, 512),
        "sd_steps": 20,
        "guidance": "depth",  # depth OR mask
    },
    "balanced": {
        "midas_model": "DPT_Hybrid",
        "yolo_model": "yolov8n.pt",
        "sam_mode": "box+prompts",
        "sd_resolution": (768, 768),
        "sd_steps": 25,
        "guidance": "keyframes",
    },
    "quality": {
        "midas_model": "DPT_Hybrid",  # DPT_Large if available
        "yolo_model": "yolov8m.pt",
        "sam_mode": "full",
        "sd_resolution": (1024, 1024),
        "sd_steps": 40,
        "guidance": "depth+mask",
    },
}


def get_preset_config(preset: str) -> dict[str, Any]:
    """Return preset config, defaulting to fast if invalid."""
    p = preset.lower() if preset else "fast"
    return PRESETS.get(p, PRESETS["fast"])
