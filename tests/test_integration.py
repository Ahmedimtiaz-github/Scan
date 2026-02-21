"""Integration tests for full pipeline."""

import os
import json
import subprocess
import sys

import pytest

# Path to scene schema for validation
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "docs", "scene_schema.json")
SAMPLE_IMAGE = os.path.join(os.path.dirname(__file__), "..", "sample_data", "sample.jpg")
OUTPUT_DIR = "outputs/integration_test"


def _ensure_sample_image():
    """Create sample_data/sample.jpg if missing."""
    if not os.path.exists(SAMPLE_IMAGE):
        os.makedirs(os.path.dirname(SAMPLE_IMAGE), exist_ok=True)
        from PIL import Image
        Image.new("RGB", (512, 512), (128, 128, 128)).save(SAMPLE_IMAGE)


def _validate_against_schema(data: dict, schema_path: str) -> bool:
    """Validate JSON against schema. Returns True if valid or schema missing."""
    if not os.path.exists(schema_path):
        return True
    try:
        import jsonschema
        with open(schema_path) as f:
            schema = json.load(f)
        jsonschema.validate(instance=data, schema=schema)
        return True
    except ImportError:
        return True  # jsonschema optional
    except Exception:
        return False


@pytest.mark.skipif(
    not os.environ.get("RUN_HEAVY"),
    reason="Full pipeline test; set RUN_HEAVY=1 to run",
)
class TestFullIntegration:
    """Full pipeline test. Skipped in CI unless RUN_HEAVY=1."""

    def test_main_image_mode_produces_outputs(self):
        """Run main in image mode and assert outputs exist."""
        _ensure_sample_image()
        cwd = os.path.dirname(os.path.dirname(__file__))
        cmd = [
            sys.executable, "-m", "src.main",
            "--mode", "image",
            "--preset", "fast",
            "--input", SAMPLE_IMAGE,
            "--output", OUTPUT_DIR,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
        assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"

        scene_json = os.path.join(cwd, OUTPUT_DIR, "scene", "frame_0001.json")
        assert os.path.exists(scene_json), f"Scene JSON not found: {scene_json}"

        with open(scene_json) as f:
            scene_data = json.load(f)
        assert _validate_against_schema(scene_data, SCHEMA_PATH), "Scene JSON invalid against schema"

        styled_path = os.path.join(cwd, OUTPUT_DIR, "frame_0001_styled.png")
        assert os.path.exists(styled_path), f"Styled image not found: {styled_path}"
        assert os.path.getsize(styled_path) > 100, "Styled image too small"

        video_path = os.path.join(cwd, OUTPUT_DIR, "final_video.mp4")
        placeholder_path = os.path.join(cwd, OUTPUT_DIR, "video_placeholder.txt")
        assert os.path.exists(video_path) or os.path.exists(placeholder_path), "Video or placeholder required"


class TestIntegrationLightweight:
    """Lightweight integration tests that run in CI (no heavy models)."""

    def test_orchestrator_with_placeholders(self):
        """Run pipeline with placeholder mode (no heavy libs); produces valid outputs."""
        _ensure_sample_image()
        cwd = os.path.dirname(os.path.dirname(__file__))
        cmd = [
            sys.executable, "-m", "src.main",
            "--mode", "image",
            "--preset", "fast",
            "--input", SAMPLE_IMAGE,
            "--output", OUTPUT_DIR,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
        assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"

        scene_json = os.path.join(cwd, OUTPUT_DIR, "scene", "frame_0001.json")
        styled_path = os.path.join(cwd, OUTPUT_DIR, "frame_0001_styled.png")
        video_path = os.path.join(cwd, OUTPUT_DIR, "final_video.mp4")
        placeholder_path = os.path.join(cwd, OUTPUT_DIR, "video_placeholder.txt")

        assert os.path.exists(scene_json), f"Scene JSON not found: {scene_json}"
        assert os.path.exists(styled_path), f"Styled image not found: {styled_path}"
        assert os.path.getsize(styled_path) > 100, "Styled image too small"
        assert os.path.exists(video_path) or os.path.exists(placeholder_path), "Video or placeholder required"

        with open(scene_json) as f:
            scene_data = json.load(f)
        assert _validate_against_schema(scene_data, SCHEMA_PATH), "Scene JSON invalid"

    def test_main_help(self):
        """CLI help works."""
        result = subprocess.run(
            [sys.executable, "-m", "src.main", "--help"],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(__file__)),
        )
        assert result.returncode == 0
        assert "mode" in result.stdout
        assert "preset" in result.stdout

    def test_main_missing_input_fails(self):
        """Missing --input fails."""
        result = subprocess.run(
            [sys.executable, "-m", "src.main", "--mode", "image"],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(__file__)),
        )
        assert result.returncode != 0
