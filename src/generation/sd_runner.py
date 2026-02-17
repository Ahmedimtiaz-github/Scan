import os
import torch
import logging
import time
from PIL import Image
from diffusers import (
    StableDiffusionControlNetImg2ImgPipeline,
    ControlNetModel,
    UniPCMultistepScheduler
)

from src.optimizations import set_cpu_optimizations, enable_channels_last
from src.prompt.prompt_generator import PromptGenerator


# -------------------- Logging --------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class StableDiffusionRunner:
    """
    CPU-optimized Stable Diffusion + ControlNet runner
    """

    PRESETS = {
        "fast": {
            "resolution": (512, 512),
            "steps": 20,
            "guidance_scale": 7.5,
            "controlnet_type": "depth"
        },
        "balanced": {
            "resolution": (768, 768),
            "steps": 25,
            "guidance_scale": 7.5,
            "controlnet_type": "depth"
        },
        "quality": {
            # Safer CPU max resolution
            "resolution": (768, 768),
            "steps": 40,
            "guidance_scale": 8.0,
            "controlnet_type": "depth"
        }
    }

    def __init__(
        self,
        model_id="runwayml/stable-diffusion-v1-5",
        controlnet_id="lllyasviel/sd-controlnet-depth"
    ):
        self.device = "cpu"
        set_cpu_optimizations()

        logger.info(f"Loading ControlNet: {controlnet_id}")
        self.controlnet = ControlNetModel.from_pretrained(
            controlnet_id,
            torch_dtype=torch.float32
        ).to(self.device)

        logger.info(f"Loading Stable Diffusion Pipeline: {model_id}")
        self.pipe = StableDiffusionControlNetImg2ImgPipeline.from_pretrained(
            model_id,
            controlnet=self.controlnet,
            torch_dtype=torch.float32,
            safety_checker=None
        ).to(self.device)

        self.pipe.scheduler = UniPCMultistepScheduler.from_config(
            self.pipe.scheduler.config
        )

        # CPU optimizations
        self.pipe.unet = enable_channels_last(self.pipe.unet)
        self.pipe.vae = enable_channels_last(self.pipe.vae)
        self.pipe.enable_attention_slicing()

        self.prompt_gen = PromptGenerator()

        logger.info("StableDiffusionRunner initialized successfully on CPU.")


    def _load_control_image(self, source_image_path, resolution, control_type):
        """
        Loads control image depending on preset type.
        """
        base_name = os.path.splitext(source_image_path)[0]

        if control_type == "depth":
            depth_path = f"{base_name}_depth.png"

            if os.path.exists(depth_path):
                logger.info(f"Using depth map: {depth_path}")
                return Image.open(depth_path).convert("RGB").resize(resolution)

            logger.warning("Depth map not found. Falling back to source image.")

        # Fallback
        return Image.open(source_image_path).convert("RGB").resize(resolution)


    def generate_styled_image(
        self,
        scene_json_path,
        source_image_path,
        preset="fast",
        mode="auto_design",
        **kwargs
    ):
        start_time = time.time()

        # -------- 1. Preset Config --------
        preset = preset.lower()
        config = self.PRESETS.get(preset, self.PRESETS["fast"])

        resolution = config["resolution"]
        steps = config["steps"]
        guidance_scale = config["guidance_scale"]
        control_type = config["controlnet_type"]

        if preset == "quality" and self.device == "cpu":
            logger.warning("High preset selected. CPU generation may be slow.")

        # -------- 2. Prompt Generation --------
        prompt = self.prompt_gen.get_prompt(
            mode,
            scene_json_path=scene_json_path,
            **kwargs
        )

        logger.info(f"Prompt Mode: {mode}")
        logger.info(f"Final Prompt: {prompt}")

        # -------- 3. Image Preparation --------
        init_image = Image.open(source_image_path).convert("RGB").resize(resolution)
        control_image = self._load_control_image(
            source_image_path,
            resolution,
            control_type
        )

        logger.info(
            f"Generation Start | Preset: {preset} | Res: {resolution} | Steps: {steps}"
        )

        # -------- 4. Inference --------
        with torch.no_grad():
            result = self.pipe(
                prompt=prompt,
                image=init_image,
                control_image=control_image,
                num_inference_steps=steps,
                guidance_scale=guidance_scale,
                strength=0.7,
            )

        output_image = result.images[0]

        # -------- 5. Save Output --------
        output_dir = "outputs"
        os.makedirs(output_dir, exist_ok=True)

        filename = os.path.basename(source_image_path).split(".")[0]
        output_path = os.path.join(output_dir, f"{filename}_styled.png")

        output_image.save(output_path)

        total_time = time.time() - start_time
        logger.info(f"Generation completed in {total_time:.2f}s")
        logger.info(f"Saved to: {output_path}")

        return output_image, output_path


# -------------------- Singleton Wrapper --------------------

_runner_instance = None


def generate_styled_image(
    scene_json_path,
    source_image_path,
    preset="fast",
    mode="auto_design"
):
    """
    Integration-ready optimized wrapper.
    Prevents model reload on every call.
    """
    global _runner_instance

    if _runner_instance is None:
        _runner_instance = StableDiffusionRunner()

    return _runner_instance.generate_styled_image(
        scene_json_path,
        source_image_path,
        preset,
        mode
    )