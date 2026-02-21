import json
import logging
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PromptGenerator:
    """
    Generates prompts for interior styling based on different modes.
    """
    
    SAFETY_SUFFIX = "high detail, photorealistic, interior design, architectural visualization"
    
    def __init__(self):
        pass

    def generate_generic_prompt(self, style: str) -> str:
        """
        Mode 1: Generic styling based on a selected style.
        """
        valid_styles = ["modern", "minimal", "luxury"]
        if style.lower() not in valid_styles:
            logger.warning(f"Style '{style}' not in recommended list {valid_styles}. Proceeding anyway.")
        
        prompt = f"Redesign this room in a {style} interior style with improved lighting, cohesive materials, realistic textures, and professional architectural photography."
        logger.info(f"Generated Generic Prompt: {prompt}")
        return prompt

    def generate_prompt_based(self, user_input: str) -> str:
        """
        Mode 2: Prompt-Based styling using direct user input.
        """
        # Sanitize string (basic)
        sanitized_input = user_input.strip().replace("\n", " ").replace("  ", " ")
        prompt = f"{sanitized_input}, {self.SAFETY_SUFFIX}"
        logger.info(f"Generated Prompt-Based: {prompt}")
        return prompt

    def generate_auto_design_prompt(self, scene_json_path: str) -> str:
        """
        Mode 3: Auto-Design based on scene analysis.
        """
        try:
            with open(scene_json_path, 'r') as f:
                scene_data = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load scene JSON: {e}")
            return f"professional interior design, {self.SAFETY_SUFFIX}"

        # 1. Detect dominant object/room type
        objects = scene_data.get("objects", [])
        room_type = "room"
        object_labels = [obj.get("label", "").lower() for obj in objects]
        
        if any(label in ["sofa", "couch", "tv", "coffee table"] for label in object_labels):
            room_type = "living room"
        elif any(label in ["bed", "nightstand"] for label in object_labels):
            room_type = "bedroom"
        elif any(label in ["dining table", "chair"] for label in object_labels):
            room_type = "dining room"
        elif any(label in ["stove", "fridge", "counter"] for label in object_labels):
            room_type = "kitchen"

        # 2. Estimate brightness/tone
        brightness_meta = scene_data.get("brightness_metadata", {})
        is_dark = brightness_meta.get("is_dark", False)
        tone_suggestion = "bright, " if is_dark else ""

        # 3. Estimate room size/style from depth
        depth_summary = scene_data.get("depth_summary", {})
        variance = depth_summary.get("variance", 0)
        style_suggestion = "modern"
        if variance > 1.5:
            style_suggestion = "spacious modern"
        elif variance < 0.5:
            style_suggestion = "cozy minimal"

        prompt = f"Design a {tone_suggestion}{style_suggestion} {room_type} with neutral tones, improved lighting, balanced furniture placement, and natural materials."
        logger.info(f"Generated Auto-Design Prompt: {prompt}")
        return prompt

    def get_prompt(self, mode: str, **kwargs) -> str:
        """
        Main entry point to get a prompt based on mode.
        """
        if mode == "generic":
            return self.generate_generic_prompt(kwargs.get("style", "modern"))
        elif mode == "prompt_based":
            return self.generate_prompt_based(kwargs.get("user_input", ""))
        elif mode == "auto_design":
            return self.generate_auto_design_prompt(kwargs.get("scene_json_path", ""))
        else:
            logger.error(f"Unknown mode: {mode}")
            return f"professional interior design, {self.SAFETY_SUFFIX}"
