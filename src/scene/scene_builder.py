import os
import json
import numpy as np
import cv2


class SceneBuilder:
    def __init__(self):
        print("[INFO] SceneBuilder initialized")

    def build_scene(self, depth_norm, detections, mask_paths, output_path):
        """
        depth_norm: normalized depth map (0–1 float array)
        detections: YOLO detections list
        mask_paths: list of mask image paths
        """

        scene_objects = []

        for idx, det in enumerate(detections):
            mask = cv2.imread(mask_paths[idx], cv2.IMREAD_GRAYSCALE)

            # Resize mask if needed
            if mask.shape != depth_norm.shape:
                mask = cv2.resize(mask, (depth_norm.shape[1], depth_norm.shape[0]))

            mask_binary = mask > 0

            # Compute average depth inside mask
            if np.sum(mask_binary) > 0:
                avg_depth = float(np.mean(depth_norm[mask_binary]))
            else:
                avg_depth = 0.0

            obj_data = {
                "object_id": idx + 1,
                "bbox": det["bbox"],
                "class_id": det["class_id"],
                "confidence": det["confidence"],
                "average_depth": avg_depth
            }

            scene_objects.append(obj_data)

        scene = {
            "frame_id": "frame_0001",
            "objects": scene_objects
        }

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(scene, f, indent=4)

        print(f"[INFO] Scene saved at {output_path}")

        return scene
