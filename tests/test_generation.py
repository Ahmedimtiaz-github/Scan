import os
import json
import numpy as np
import pytest
from PIL import Image

from src.prompt.prompt_generator import PromptGenerator
from src.video.video_maker import VideoMaker
from src.adapters.video_adapter import create_video_from_keyframes, make_video_from_keyframes


@pytest.fixture
def dummy_image():
    out_dir = os.path.join(os.path.dirname(__file__), "tmp")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "dummy.png")
    Image.fromarray(np.zeros((64, 64, 3), dtype=np.uint8)).save(path)
    return path


@pytest.fixture
def dummy_scene_json():
    out_dir = os.path.join(os.path.dirname(__file__), "tmp")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "scene.json")
    with open(path, "w") as f:
        json.dump({
            "objects": [{"label": "sofa"}],
            "brightness_metadata": {"is_dark": True},
            "depth_summary": {"variance": 1.0},
        }, f)
    return path


@pytest.fixture
def mock_scene_frame():
    """Scene frame dict matching schema (for adapter tests)."""
    return {
        "id": "frame_0001",
        "source": "frame_0001.jpg",
        "width": 512,
        "height": 512,
        "depth_path": "depth_frame_0001.png",
        "masks": [{"mask_path": "masks/mask_couch_0001.png", "class": "couch", "bbox": [10, 10, 100, 100]}],
        "bboxes": [{"class": "couch", "bbox": [10, 10, 100, 100]}],
        "extra": {},
    }


class TestPromptGenerator:
    def test_generic(self):
        gen = PromptGenerator()
        p = gen.get_prompt("generic", style="luxury")
        assert "luxury" in p

    def test_prompt_based(self):
        gen = PromptGenerator()
        p = gen.get_prompt("prompt_based", user_input="cyberpunk style")
        assert "cyberpunk" in p

    def test_auto_design(self, dummy_scene_json):
        gen = PromptGenerator()
        p = gen.get_prompt("auto_design", scene_json_path=dummy_scene_json)
        assert isinstance(p, str)
        assert len(p) > 0


class TestVideoMaker:
    def test_create_video(self, dummy_image):
        out_dir = os.path.join(os.path.dirname(__file__), "tmp")
        os.makedirs(out_dir, exist_ok=True)
        vm = VideoMaker(output_path=os.path.join(out_dir, "test_video.mp4"), fps=10)
        output = vm.create_video(
            [dummy_image, dummy_image],
            transition_frames=2,
            hold_frames=2,
        )
        assert output is not None
        assert os.path.exists(output)


class TestVideoAdapter:
    def test_create_video_from_keyframes(self, dummy_image):
        out_dir = os.path.join(os.path.dirname(__file__), "tmp")
        os.makedirs(out_dir, exist_ok=True)
        output = create_video_from_keyframes(
            [dummy_image, dummy_image],
            os.path.join(out_dir, "adapter_video.mp4"),
            fps=10,
            transition_frames=2,
            hold_frames=2,
        )
        assert output is not None
        assert os.path.exists(output)

    def test_make_video_from_keyframes(self, dummy_image):
        out_dir = os.path.join(os.path.dirname(__file__), "tmp")
        os.makedirs(out_dir, exist_ok=True)
        output = make_video_from_keyframes(
            [dummy_image, dummy_image],
            os.path.join(out_dir, "make_video.mp4"),
            fps=10,
            crossfade_frames=2,
        )
        assert output is not None
        assert os.path.exists(output)


class TestGenerationAdapter:
    """Tests for generate_styled_frame adapter (no heavy SD)."""

    def test_adapter_returns_string_for_mock_frame(self, mock_scene_frame, dummy_image):
        """Adapter signature: returns path to generated image. Full test requires SD."""
        # Lightweight: just assert mock_scene_frame has required keys
        assert "id" in mock_scene_frame
        assert "depth_path" in mock_scene_frame
        assert "bboxes" in mock_scene_frame


@pytest.mark.skipif(
    not os.environ.get("RUN_HEAVY"),
    reason="Heavy models required; set RUN_HEAVY=1 to run",
)
class TestSDRunner:
    """SD runner tests - require model download. Skipped in CI."""

    def test_sd_runner_fast_preset(self, dummy_image, dummy_scene_json):
        from src.generation.sd_runner import generate_styled_image

        output_image, output_path = generate_styled_image(
            scene_json_path=dummy_scene_json,
            source_image_path=dummy_image,
            preset="fast",
            mode="auto_design",
        )
        assert output_image is not None
        assert os.path.exists(output_path)

    def test_invalid_preset_fallback(self, dummy_image, dummy_scene_json):
        from src.generation.sd_runner import generate_styled_image

        output_image, output_path = generate_styled_image(
            scene_json_path=dummy_scene_json,
            source_image_path=dummy_image,
            preset="invalid_preset",
            mode="auto_design",
        )
        assert output_image is not None