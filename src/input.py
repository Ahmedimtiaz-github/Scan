"""
Video frame extraction and sampling utilities.
Batool's module - used by orchestrator for video mode.
"""

import os
import logging
import cv2

logger = logging.getLogger(__name__)


def extract_frames(
    video_path: str,
    output_dir: str,
    fps: float = 1.0,
    max_frames: int = 10,
) -> list[str]:
    """
    Extract frames from video at given sampling rate.

    Args:
        video_path: Path to input video file.
        output_dir: Directory to save extracted frames.
        fps: Sampling rate (frames per second). Default 1.0 for Fast preset.
        max_frames: Maximum number of frames to extract. Default 10 for CPU mode.

    Returns:
        List of paths to extracted frame images (frame_0001.jpg, frame_0002.jpg, ...).
    """
    os.makedirs(output_dir, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")

    video_fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    frame_interval = max(1, int(video_fps / fps)) if fps > 0 else 1

    frame_paths = []
    frame_count = 0
    saved_count = 0

    while saved_count < max_frames:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            idx = saved_count + 1
            frame_filename = f"frame_{idx:04d}.jpg"
            frame_path = os.path.join(output_dir, frame_filename)
            cv2.imwrite(frame_path, frame)
            frame_paths.append(frame_path)
            saved_count += 1
            logger.info(f"Extracted frame {saved_count}/{max_frames}: {frame_path}")

        frame_count += 1

    cap.release()
    logger.info(f"Extracted {len(frame_paths)} frames from {video_path}")
    return frame_paths
