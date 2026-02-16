# src/config.py
# Preset mapping and common configuration used by orchestrator
PRESETS = {
    "fast": {
        "midas": "midas_v2_small",
        "yolo": "yolov8n",
        "sam": "sam_box",
        "sd_res": [512,512],
        "sd_steps": 20,
        "guidance": "depth_or_mask"
    },
    "balanced": {
        "midas": "dpt_hybrid",
        "yolo": "yolov8n",
        "sam": "sam_box_prompts",
        "sd_res": [768,768],
        "sd_steps": 25,
        "guidance": "depth_plus_mask_on_keyframes"
    },
    "quality": {
        "midas": "dpt_large",
        "yolo": "yolov8m",
        "sam": "sam_full",
        "sd_res": [1024,1024],
        "sd_steps": 40,
        "guidance": "depth_and_mask"
    }
}
