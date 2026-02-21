"""
Perception adapter: normalizes outputs from MiDaS, YOLO, SAM to scene schema.
Heavy imports deferred until run_perception_for_image() so module can be imported without torch etc.
"""

import os
import logging
import shutil
import time
from typing import Any

import cv2
import numpy as np

from src.config import get_preset_config

logger = logging.getLogger(__name__)

# COCO 80-class names (YOLOv8 default)
COCO_CLASSES = [
    "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck",
    "boat", "traffic light", "fire hydrant", "stop sign", "parking meter", "bench",
    "bird", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra",
    "giraffe", "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee",
    "skis", "snowboard", "sports ball", "kite", "baseball bat", "baseball glove",
    "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
    "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange",
    "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair", "couch",
    "potted plant", "bed", "dining table", "toilet", "tv", "laptop", "mouse",
    "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink",
    "refrigerator", "book", "clock", "vase", "scissors", "teddy bear", "hair drier",
    "toothbrush",
]


def _expand_bbox(bbox: list[float], img_w: int, img_h: int, expand_pct: float = 0.1) -> np.ndarray:
    """Expand bbox by percentage, clamped to image bounds."""
    x1, y1, x2, y2 = bbox
    w, h = x2 - x1, y2 - y1
    pad_w, pad_h = w * expand_pct / 2, h * expand_pct / 2
    x1 = max(0, x1 - pad_w)
    y1 = max(0, y1 - pad_h)
    x2 = min(img_w, x2 + pad_w)
    y2 = min(img_h, y2 + pad_h)
    return np.array([x1, y1, x2, y2])


def _create_placeholder_frame(image_path: str, out_dir: str, frame_id: str) -> dict:
    """Create minimal valid frame when heavy libs unavailable."""
    import cv2
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Cannot read image: {image_path}")
    height, width = image.shape[:2]
    frame_dir = os.path.join(out_dir, "frames", frame_id)
    os.makedirs(frame_dir, exist_ok=True)
    depth_path = os.path.join(frame_dir, f"depth_{frame_id}.png")
    cv2.imwrite(depth_path, image)  # Use image as placeholder depth
    depth_path_rel = os.path.join("frames", frame_id, f"depth_{frame_id}.png").replace("\\", "/")
    return {
        "id": frame_id,
        "source": os.path.basename(image_path),
        "width": width,
        "height": height,
        "depth_path": depth_path_rel,
        "masks": [],
        "bboxes": [],
        "extra": {"placeholder": True},
    }


def run_perception_for_image(image_path: str, out_dir: str, preset: str, frame_id: str = "frame_0001") -> dict:
    """
    Run full perception pipeline: MiDaS -> YOLO -> SAM, return scene frame dict.
    Saves under out_dir/frames/frame_{id}/ and writes out_dir/scene/frame_{id}.json.
    If heavy libs unavailable, returns minimal placeholder frame.
    """
    try:
        from src.depth.midas_runner import MiDaSRunner
        from src.detection.yolov8_runner import YOLOv8Runner
        from src.segmentation.sam_runner import SAMRunner
    except (ImportError, ModuleNotFoundError) as e:
        logger.warning(f"Heavy perception libs unavailable: {e}")
        return _create_placeholder_frame(image_path, out_dir, frame_id)

    config = get_preset_config(preset)
    frame_dir = os.path.join(out_dir, "frames", frame_id)
    scene_dir = os.path.join(out_dir, "scene")
    os.makedirs(frame_dir, exist_ok=True)
    os.makedirs(scene_dir, exist_ok=True)
    masks_dir = os.path.join(frame_dir, "masks")
    os.makedirs(masks_dir, exist_ok=True)

    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Cannot read image: {image_path}")

    height, width = image.shape[:2]
    source_name = os.path.basename(image_path)
    logger.info(f"Perception: image {width}x{height}")

    # 1. MiDaS depth
    t0 = time.perf_counter()
    depth_filename = f"depth_{frame_id}.png"
    depth_path_full = os.path.join(frame_dir, depth_filename)
    midas_runner = MiDaSRunner(model_type=config.get("midas_model", "MiDaS_small"))
    _, depth_norm = midas_runner.run(image, depth_path_full)
    depth_path_rel = os.path.join("frames", frame_id, depth_filename).replace("\\", "/")
    logger.info(f"MiDaS took {time.perf_counter() - t0:.1f}s")

    # 2. YOLO detection
    t0 = time.perf_counter()
    detections_filename = f"detections_{frame_id}.json"
    detections_path = os.path.join(frame_dir, detections_filename)
    yolo_runner = YOLOv8Runner(model_name=config.get("yolo_model", "yolov8n.pt"))
    detections = yolo_runner.run(image, detections_path)
    logger.info(f"YOLO took {time.perf_counter() - t0:.1f}s, {len(detections)} detections")

    # Map class_id to class name
    detections_with_class = []
    for d in detections:
        cid = d.get("class_id", 0)
        class_name = COCO_CLASSES[cid] if 0 <= cid < len(COCO_CLASSES) else f"obj_{cid}"
        detections_with_class.append({**d, "class": class_name})

    # 3. SAM on each bbox (expand by 10%)
    sam_detections = []
    for d in detections_with_class:
        bbox = d["bbox"]
        expanded = _expand_bbox(bbox, width, height, 0.1)
        sam_detections.append({"bbox": expanded.tolist(), "class": d["class"], "confidence": d.get("confidence", 0)})

    if sam_detections:
        t0 = time.perf_counter()
        sam_runner = SAMRunner()
        sam_detections_for_runner = [{"bbox": d["bbox"]} for d in sam_detections]
        mask_paths_raw = sam_runner.run(image, sam_detections_for_runner, masks_dir)

        masks_list = []
        for idx, (det, raw_path) in enumerate(zip(sam_detections, mask_paths_raw)):
            class_safe = det["class"].replace(" ", "_")
            new_name = f"mask_{class_safe}_{idx + 1:04d}.png"
            new_path = os.path.join(masks_dir, new_name)
            if raw_path != new_path:
                shutil.move(raw_path, new_path)
            masks_list.append({
                "mask_path": os.path.join("frames", frame_id, "masks", new_name).replace("\\", "/"),
                "class": det["class"],
                "bbox": det["bbox"],
            })
        logger.info(f"SAM took {time.perf_counter() - t0:.1f}s, {len(masks_list)} masks")
    else:
        masks_list = []

    bboxes_list = [{"class": d["class"], "bbox": d["bbox"]} for d in detections_with_class]

    frame_obj: dict[str, Any] = {
        "id": frame_id,
        "source": source_name,
        "width": width,
        "height": height,
        "depth_path": depth_path_rel,
        "masks": masks_list,
        "bboxes": bboxes_list,
        "extra": {},
    }

    return frame_obj
