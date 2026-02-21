"""
Generation adapter: bridges scene frame dict to sd_runner.
Ensures depth path and scene JSON are compatible with PromptGenerator/sd_runner.
"""

import json
import os
import tempfile
import shutil
import logging
from typing import Any

from src.config import get_preset_config
from src.generation.sd_runner import generate_styled_image

logger = logging.getLogger(__name__)


def _build_prompt_compatible_scene(scene_frame: dict, output_dir: str) -> dict:
    """Build scene dict compatible with PromptGenerator (objects, brightness_metadata, depth_summary)."""
    objects = []
    for b in scene_frame.get("bboxes", []):
        objects.append({
            "label": b.get("class", "object"),
            "bbox": b.get("bbox", []),
            "confidence": 0.9,
        })
    for m in scene_frame.get("masks", []):
        # Avoid duplicates if already in bboxes
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


def generate_styled_frame(
    scene_frame: dict,
    source_image: str,
    out_path: str,
    preset: str,
) -> str:
    """
    Generate styled image from scene frame using sd_runner.

    Args:
        scene_frame: Scene frame dict (from perception_adapter).
        source_image: Path to source frame image.
        out_path: Path to save generated image.
        preset: fast | balanced | quality.

    Returns:
        Path to generated image (out_path).
    """
    config = get_preset_config(preset)
    output_dir = os.path.dirname(out_path)
    os.makedirs(output_dir, exist_ok=True)

    # 1. Copy depth to where sd_runner expects it: {source_base}_depth.png
    source_base = os.path.splitext(source_image)[0]
    depth_path_rel = scene_frame.get("depth_path", "")
    depth_dst = f"{source_base}_depth.png"
    if depth_path_rel:
        # Depth is at output_dir/scene/depth_frame_XXXX.png (scene written by orchestrator)
        out_dir = os.path.dirname(out_path)
        depth_src_full = os.path.join(out_dir, "scene", depth_path_rel)
        if os.path.exists(depth_src_full):
            shutil.copy2(depth_src_full, depth_dst)
            logger.info(f"Copied depth to {depth_dst} for sd_runner")

    # 2. Write temp scene JSON for PromptGenerator
    prompt_scene = _build_prompt_compatible_scene(scene_frame, output_dir)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(prompt_scene, f, indent=2)
        scene_json_path = f.name

    try:
        # 3. Call sd_runner
        output_image, result_path = generate_styled_image(
            scene_json_path=scene_json_path,
            source_image_path=source_image,
            preset=preset,
            mode="auto_design",
        )

        # 4. Copy result to out_path (sd_runner saves to outputs/{filename}_styled.png)
        if result_path != out_path:
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            shutil.copy2(result_path, out_path)
            logger.info(f"Saved styled image to {out_path}")
        return out_path
    finally:
        if os.path.exists(scene_json_path):
            os.unlink(scene_json_path)
