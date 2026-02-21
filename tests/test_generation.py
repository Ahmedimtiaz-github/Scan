import unittest
import os
import json
import numpy as np
from PIL import Image

from src.prompt.prompt_generator import PromptGenerator
from src.video.video_maker import VideoMaker
from src.generation.sd_runner import generate_styled_image

class TestGenerationStack(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        os.makedirs("tests/tmp", exist_ok=True)

        # Dummy Image
        cls.dummy_image_path = "tests/tmp/dummy.png"
        dummy_img = Image.fromarray(np.zeros((512, 512, 3), dtype=np.uint8))
        dummy_img.save(cls.dummy_image_path)

        # Dummy Scene JSON
        cls.dummy_json_path = "tests/tmp/scene.json"
        with open(cls.dummy_json_path, 'w') as f:
            json.dump({
                "objects": [{"label": "sofa"}],
                "brightness_metadata": {"is_dark": True},
                "depth_summary": {"variance": 1.0}
            }, f)

    # ----------------------# Prompt Tests
    def test_prompt_generator(self):
        gen = PromptGenerator()

        # Generic
        p1 = gen.get_prompt("generic", style="luxury")
        self.assertIn("luxury", p1)

        # Prompt-Based
        p2 = gen.get_prompt("prompt_based", user_input="cyberpunk style")
        self.assertIn("cyberpunk", p2)

        # Auto-Design
        p3 = gen.get_prompt("auto_design", scene_json_path=self.dummy_json_path)
        self.assertIsInstance(p3, str)
        self.assertTrue(len(p3) > 0)

    # ---------------------- # Video Test
    def test_video_maker(self):
        vm = VideoMaker(output_path="tests/tmp/test_video.mp4", fps=10)
        output = vm.create_video(
            [self.dummy_image_path, self.dummy_image_path],
            transition_frames=2,
            hold_frames=2
        )
        self.assertTrue(os.path.exists(output))

    # ---------------------- # SD Runner Test
    def test_sd_runner_fast_preset(self):
        output_image, output_path = generate_styled_image(
            scene_json_path=self.dummy_json_path,
            source_image_path=self.dummy_image_path,
            preset="fast",
            mode="auto_design"
        )

        self.assertIsNotNone(output_image)
        self.assertTrue(os.path.exists(output_path))
    
    # ---------------------- # Preset Fallback Test
    def test_invalid_preset_fallback(self):
        output_image, output_path = generate_styled_image(
            scene_json_path=self.dummy_json_path,
            source_image_path=self.dummy_image_path,
            preset="invalid_preset",
            mode="auto_design"
        )

        self.assertIsNotNone(output_image)


if __name__ == "__main__":
    unittest.main()