"""
Adapter modules for normalizing perception and generation outputs.
"""

__all__ = [
    "run_perception_for_image",
    "generate_styled_frame",
    "create_video_from_keyframes",
    "make_video_from_keyframes",
]


def __getattr__(name):
    if name == "run_perception_for_image":
        from src.adapters.perception_adapter import run_perception_for_image
        return run_perception_for_image
    if name == "generate_styled_frame":
        from src.adapters.generation_adapter import generate_styled_frame
        return generate_styled_frame
    if name == "create_video_from_keyframes":
        from src.adapters.video_adapter import create_video_from_keyframes
        return create_video_from_keyframes
    if name == "make_video_from_keyframes":
        from src.adapters.video_adapter import make_video_from_keyframes
        return make_video_from_keyframes
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
