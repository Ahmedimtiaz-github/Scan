"""Tests for perception adapter and input module."""

import os
import json
import pytest
import numpy as np
from unittest.mock import patch, MagicMock

from src.input import extract_frames
from src.config import get_preset_config, PRESETS


class TestConfig:
    def test_get_preset_config_fast(self):
        cfg = get_preset_config("fast")
        assert cfg["midas_model"] == "MiDaS_small"
        assert cfg["sd_resolution"] == (512, 512)
        assert cfg["sd_steps"] == 20

    def test_get_preset_config_balanced(self):
        cfg = get_preset_config("balanced")
        assert cfg["midas_model"] == "DPT_Hybrid"
        assert cfg["sd_resolution"] == (768, 768)

    def test_get_preset_config_invalid_fallback(self):
        cfg = get_preset_config("invalid")
        assert cfg == PRESETS["fast"]


class TestInput:
    def test_extract_frames_creates_video(self):
        """Create a minimal video and extract frames."""
        import cv2
        out_dir = os.path.join(os.path.dirname(__file__), "tmp")
        os.makedirs(out_dir, exist_ok=True)
        video_path = os.path.join(out_dir, "test_video.mp4")
        cap = cv2.VideoWriter(
            video_path,
            cv2.VideoWriter_fourcc(*"mp4v"),
            10,
            (64, 64),
        )
        for _ in range(30):
            cap.write(np.zeros((64, 64, 3), dtype=np.uint8))
        cap.release()

        frames_dir = os.path.join(out_dir, "frames")
        paths = extract_frames(video_path, frames_dir, fps=5, max_frames=3)
        assert len(paths) >= 1
        assert all(os.path.exists(p) for p in paths)

    def test_extract_frames_invalid_video(self):
        with pytest.raises(ValueError, match="Cannot open"):
            extract_frames("/nonexistent/video.mp4", "output")


@pytest.mark.skipif(
    not os.environ.get("RUN_HEAVY"),
    reason="Heavy models required; set RUN_HEAVY=1 to run",
)
class TestPerceptionAdapter:
    """Tests that require MiDaS, YOLO, SAM. Skipped in CI by default."""

    def test_run_perception_for_image_return_type(self):
        from src.adapters.perception_adapter import run_perception_for_image

        out_dir = os.path.join(os.path.dirname(__file__), "tmp")
        os.makedirs(out_dir, exist_ok=True)
        img_path = os.path.join(out_dir, "test.jpg")
        cv2 = __import__("cv2")
        cv2.imwrite(img_path, np.zeros((64, 64, 3), dtype=np.uint8))

        scene_dir = os.path.join(out_dir, "scene")
        result = run_perception_for_image(
            img_path, scene_dir, "fast", frame_id="frame_0001"
        )

        assert isinstance(result, dict)
        assert "id" in result
        assert "source" in result
        assert "width" in result
        assert "height" in result
        assert "depth_path" in result
        assert "masks" in result
        assert "bboxes" in result
        assert result["id"] == "frame_0001"
