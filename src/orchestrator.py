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
