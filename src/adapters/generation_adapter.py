"""
Generation adapter: bridges scene frame dict to sd_runner.
Ensures depth path and scene JSON are compatible with PromptGenerator/sd_runner.
Creates deterministic placeholder if model unavailable.
"""

import json
import os
import tempfile
import shutil
import logging
from typing import Any

from src.config import get_preset_config

logger = logging.getLogger(__name__)


def _build_prompt_compatible_scene(scene_frame: dict, output_dir: str) -> dict:
    """Build scene dict compatible with PromptGenerator."""
    objects = []
    for b in scene_frame.get("bboxes", []):
        objects.append({
            "label": b.get("class", "object"),
            "bbox": b.get("bbox", []),
            "confidence": 0.9,
        })
    for m in scene_frame.get("masks", []):
        if not any(o.get("label") == m.get("class") for o in objects):
            objects.append({
                "label": m.get("class", "object"),
                "bbox": m.get("bbox", []),
                "confidence": 0.9,
            })
    return {
        "objects": objects,
        "brightness_metadata": {"is_dark": False, "average_brightness": 128},
        "depth_summary": {"variance": 1.0, "min_depth": 0.0, "max_depth": 1.0},
    }


def _create_deterministic_placeholder(out_path: str, size: tuple[int, int] = (512, 512)) -> str:
    """Create deterministic 512x512 PNG and .placeholder file."""
    try:
        import numpy as np
        from PIL import Image
        # Simple gradient (deterministic)
        arr = np.zeros((size[1], size[0], 3), dtype=np.uint8)
        for y in range(size[1]):
            for x in range(size[0]):
                arr[y, x] = [
                    (x * 255 // size[0]) % 256,
                    (y * 255 // size[1]) % 256,
                    128,
                ]
        img = Image.fromarray(arr)
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        img.save(out_path)
        placeholder_marker = out_path + ".placeholder"
        with open(placeholder_marker, "w") as f:
            f.write("Deterministic placeholder (model unavailable)\n")
        logger.warning(f"Model unavailable: created placeholder at {out_path}")
        return out_path
    except Exception as e:
        logger.exception(f"Could not create placeholder: {e}")
        raise


def generate_styled_frame(
    scene_frame: dict,
    source_image: str,
    out_path: str,
    preset: str,
) -> str:
    """
    Generate styled image from scene frame using sd_runner.
    On model unavailability: create deterministic placeholder and return out_path.
    """
    config = get_preset_config(preset)
    output_dir = os.path.dirname(out_path)
    os.makedirs(output_dir, exist_ok=True)
    resolution = config.get("sd_resolution", (512, 512))

    # 1. Copy depth to where sd_runner expects it: {source_base}_depth.png
    source_base = os.path.splitext(source_image)[0]
    depth_path_rel = scene_frame.get("depth_path", "")
    depth_dst = f"{source_base}_depth.png"
    if depth_path_rel:
        depth_src_full = os.path.join(output_dir, depth_path_rel)
        if not os.path.exists(depth_src_full):
            depth_src_full = os.path.join(os.path.dirname(output_dir), depth_path_rel)
        if os.path.exists(depth_src_full):
            shutil.copy2(depth_src_full, depth_dst)
            logger.info(f"Copied depth to {depth_dst}")

    # 2. Write temp scene JSON
    prompt_scene = _build_prompt_compatible_scene(scene_frame, output_dir)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(prompt_scene, f, indent=2)
        scene_json_path = f.name

    try:
        from src.generation.sd_runner import generate_styled_image

        output_image, result_path = generate_styled_image(
            scene_json_path=scene_json_path,
            source_image_path=source_image,
            preset=preset,
            mode="auto_design",
        )

        if result_path != out_path:
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            shutil.copy2(result_path, out_path)
        return out_path

    except (ImportError, ModuleNotFoundError) as e:
        logger.warning(f"Heavy deps not available: {e}")
        return _create_deterministic_placeholder(out_path, resolution)
    except Exception as e:
        logger.warning(f"Generation failed: {e}")
        return _create_deterministic_placeholder(out_path, resolution)
    finally:
        if os.path.exists(scene_json_path):
            os.unlink(scene_json_path)
