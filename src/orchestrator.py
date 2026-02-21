"""
High-level pipeline controller: wires perception -> generation -> video.
"""

import os
import json
import logging
import sys
from datetime import datetime
from typing import Optional

from src.input import extract_frames
from src.adapters.perception_adapter import run_perception_for_image
from src.adapters.generation_adapter import generate_styled_frame
from src.adapters.video_adapter import create_video_from_keyframes
from src.video.video_maker import VideoMaker

logger = logging.getLogger(__name__)


class OrchestratorLogger:
    """Capture logs to file while also printing."""

    def __init__(self, log_path: str):
        self.log_path = log_path
        self.file_handler: Optional[logging.FileHandler] = None

    def setup(self):
        os.makedirs(os.path.dirname(self.log_path) or ".", exist_ok=True)
        self.file_handler = logging.FileHandler(self.log_path, mode="w", encoding="utf-8")
        self.file_handler.setLevel(logging.INFO)
        self.file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        logging.getLogger().addHandler(self.file_handler)

    def teardown(self):
        if self.file_handler:
            logging.getLogger().removeHandler(self.file_handler)
            self.file_handler.close()


def run(
    mode: str,
    preset: str,
    input_path: str,
    output_dir: str,
    fps: float = 1.0,
    max_frames: int = 10,
) -> None:
    """
    Run full pipeline: perception -> generation -> video.

    Args:
        mode: "image" or "video".
        preset: "fast" | "balanced" | "quality".
        input_path: Path to input image or video.
        output_dir: Output directory for all outputs.
        fps: Frame sampling rate for video mode (default 1.0).
        max_frames: Max keyframes for video mode (default 10).
    """
    orch_logger = OrchestratorLogger(os.path.join(output_dir, "run.log"))
    orch_logger.setup()

    start_time = datetime.now()
    logger.info(f"Pipeline start | mode={mode} preset={preset} input={input_path}")

    os.makedirs(output_dir, exist_ok=True)
    scene_dir = os.path.join(output_dir, "scene")
    os.makedirs(scene_dir, exist_ok=True)

    # 1. Get frame list
    if mode.lower() == "image":
        frame_paths = [input_path]
        frames_dir = os.path.dirname(input_path)
    else:
        frames_dir = os.path.join(output_dir, "frames")
        frame_paths = extract_frames(input_path, frames_dir, fps=fps, max_frames=max_frames)
        if not frame_paths:
            logger.error("No frames extracted from video.")
            orch_logger.teardown()
            return

    # 2. Process each frame: perception -> generation
    styled_paths = []
    all_frames = []

    for idx, frame_path in enumerate(frame_paths):
        frame_id = f"frame_{idx + 1:04d}"
        step_start = datetime.now()

        try:
            # Perception
            frame_obj = run_perception_for_image(frame_path, scene_dir, preset, frame_id=frame_id)
            frame_obj["preset"] = preset
            frame_obj["mode"] = mode
            all_frames.append(frame_obj)

            scene_frame_path = os.path.join(scene_dir, f"{frame_id}.json")
            with open(scene_frame_path, "w") as f:
                json.dump({"frames": [frame_obj], "preset": preset, "mode": mode}, f, indent=2)

            step_elapsed = (datetime.now() - step_start).total_seconds()
            logger.info(f"Perception for {frame_id} took {step_elapsed:.1f}s")

            # Generation
            out_styled = os.path.join(output_dir, f"{frame_id}_styled.png")
            try:
                generate_styled_frame(frame_obj, frame_path, out_styled, preset)
                styled_paths.append(out_styled)
            except Exception as e:
                logger.exception(f"Generation failed for {frame_id}: {e}")
                placeholder = os.path.join(output_dir, f"{frame_id}_styled_error.png")
                try:
                    import cv2
                    img = cv2.imread(frame_path)
                    if img is not None:
                        cv2.imwrite(placeholder, img)
                except Exception:
                    pass
                styled_paths.append(placeholder)

        except Exception as e:
            logger.exception(f"Perception failed for {frame_id}: {e}")
            continue

    # 3. Assemble video
    if styled_paths:
        video_path = os.path.join(output_dir, "final_video.mp4")
        try:
            vm = VideoMaker(output_path=video_path, fps=24)
            vm.create_video(styled_paths, transition_frames=12, hold_frames=24)
        except Exception as e:
            logger.warning(f"VideoMaker failed, trying adapter: {e}")
            create_video_from_keyframes(styled_paths, video_path, fps=24)

    # Optional: combined scene.json
    combined_scene_path = os.path.join(scene_dir, "scene.json")
    with open(combined_scene_path, "w") as f:
        json.dump({"frames": all_frames, "preset": preset, "mode": mode}, f, indent=2)

    total_elapsed = (datetime.now() - start_time).total_seconds()
    logger.info(f"Pipeline complete in {total_elapsed:.1f}s")
    orch_logger.teardown()
