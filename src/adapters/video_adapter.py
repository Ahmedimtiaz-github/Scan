"""
Video adapter: fallback cross-dissolve video maker using OpenCV.
Used when video_maker is not available or needs different interface.
"""

import os
import logging
import cv2

logger = logging.getLogger(__name__)


def make_video_from_keyframes(
    keyframe_paths: list[str],
    out_video_path: str,
    fps: int = 24,
    crossfade_frames: int = 6,
) -> str | None:
    """
    Create video from styled keyframes using cross-dissolve.
    CPU-friendly crossfade between keyframes.
    """
    return create_video_from_keyframes(
        keyframe_paths,
        out_video_path,
        fps=fps,
        transition_frames=crossfade_frames,
        hold_frames=max(6, crossfade_frames * 2),
    )


def create_video_from_keyframes(
    keyframe_paths: list[str],
    output_path: str,
    fps: int = 24,
    transition_frames: int = 12,
    hold_frames: int = 24,
) -> str | None:
    """
    Create video from styled keyframes using cross-dissolve transitions.

    Args:
        keyframe_paths: List of paths to styled keyframe images.
        output_path: Output video path.
        fps: Output video FPS.
        transition_frames: Frames for cross-dissolve between keyframes.
        hold_frames: Frames to hold each keyframe before transition.

    Returns:
        Output path if successful, None otherwise.
    """
    if not keyframe_paths:
        logger.error("No keyframes provided for video creation.")
        return None

    first_img = cv2.imread(keyframe_paths[0])
    if first_img is None:
        logger.error(f"Could not read image: {keyframe_paths[0]}")
        return None

    height, width = first_img.shape[:2]
    size = (width, height)
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, size)

    logger.info(f"Creating video: {output_path} | Size: {size} | FPS: {fps}")

    for i in range(len(keyframe_paths)):
        img_current = cv2.imread(keyframe_paths[i])
        if img_current is None:
            continue
        if img_current.shape[:2] != (height, width):
            img_current = cv2.resize(img_current, size)

        for _ in range(hold_frames):
            out.write(img_current)

        if i < len(keyframe_paths) - 1:
            img_next = cv2.imread(keyframe_paths[i + 1])
            if img_next is not None:
                if img_next.shape[:2] != (height, width):
                    img_next = cv2.resize(img_next, size)
                for f in range(transition_frames):
                    alpha = f / transition_frames
                    blended = cv2.addWeighted(img_current, 1 - alpha, img_next, alpha, 0)
                    out.write(blended)

    out.release()
    logger.info(f"Video saved to {output_path}")
    return output_path
