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
    not os.path.exists(SAMPLE_IMAGE) or not os.environ.get("RUN_HEAVY"),
    reason="Need sample_data/sample.jpg and RUN_HEAVY=1 for full integration test",
)
class TestFullIntegration:
    """Full pipeline test. Skipped in CI unless RUN_HEAVY=1 and sample exists."""

    def test_main_image_mode_produces_outputs(self):
        """Run main in image mode and assert outputs exist."""
        cmd = [
            sys.executable, "-m", "src.main",
            "--mode", "image",
            "--preset", "fast",
            "--input", SAMPLE_IMAGE,
            "--output", OUTPUT_DIR,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(__file__)))
        assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"

        scene_json = os.path.join(OUTPUT_DIR, "scene", "frame_0001.json")
        assert os.path.exists(scene_json), f"Scene JSON not found: {scene_json}"

        with open(scene_json) as f:
            scene_data = json.load(f)
        assert _validate_against_schema(scene_data, SCHEMA_PATH), "Scene JSON invalid against schema"

        styled_path = os.path.join(OUTPUT_DIR, "frame_0001_styled.png")
        assert os.path.exists(styled_path), f"Styled image not found: {styled_path}"
        assert os.path.getsize(styled_path) > 100, "Styled image too small"

        video_path = os.path.join(OUTPUT_DIR, "final_video.mp4")
        assert os.path.exists(video_path), f"Video not found: {video_path}"


class TestIntegrationLightweight:
    """Lightweight integration tests that run in CI (no heavy models)."""

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
