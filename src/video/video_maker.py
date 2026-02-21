import cv2
import numpy as np
import os
import logging

logger = logging.getLogger(__name__)

class VideoMaker:
    """
    Creates a video from styled keyframes using cross-dissolve transitions.
    """
    
    def __init__(self, output_path="outputs/video.mp4", fps=24):
        self.output_path = output_path
        self.fps = fps
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

    def create_video(self, keyframe_paths, transition_frames=12, hold_frames=24):
        """
        Creates a video by blending keyframes.
        """
        if not keyframe_paths:
            logger.error("No keyframes provided for video creation.")
            return None

        # Read first image to get dimensions
        first_img = cv2.imread(keyframe_paths[0])
        if first_img is None:
            logger.error(f"Could not read image: {keyframe_paths[0]}")
            return None
            
        height, width, layers = first_img.shape
        size = (width, height)

        # Initialize VideoWriter
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(self.output_path, fourcc, self.fps, size)

        logger.info(f"Creating video: {self.output_path} | Size: {size} | FPS: {self.fps}")

        for i in range(len(keyframe_paths)):
            img_current = cv2.imread(keyframe_paths[i])
            
            # 1. Hold current keyframe
            for _ in range(hold_frames):
                out.write(img_current)
            
            # 2. Transition to next keyframe (if not last)
            if i < len(keyframe_paths) - 1:
                img_next = cv2.imread(keyframe_paths[i+1])
                if img_next is not None:
                    for f in range(transition_frames):
                        alpha = f / transition_frames
                        blended = cv2.addWeighted(img_current, 1 - alpha, img_next, alpha, 0)
                        out.write(blended)

        out.release()
        logger.info(f"Video saved successfully to {self.output_path}")
        return self.output_path
