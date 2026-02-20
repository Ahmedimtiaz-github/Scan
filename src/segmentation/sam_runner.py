import os
import cv2
import torch
import numpy as np
from segment_anything import sam_model_registry, SamPredictor


class SAMRunner:
    def __init__(self, checkpoint_path="sam_vit_b_01ec64.pth", model_type="vit_b"):
        """
        model_type:
        - vit_b (recommended for CPU)
        """

        self.device = "cpu"

        sam = sam_model_registry[model_type](checkpoint=checkpoint_path)
        sam.to(self.device)
        sam.eval()

        self.predictor = SamPredictor(sam)

        print(f"[INFO] Loaded SAM {model_type} on CPU")

    def run(self, image, detections, output_dir):
        """
        image: numpy BGR image
        detections: list from YOLO (bbox format: [x1, y1, x2, y2])
        output_dir: folder to save masks
        """

        os.makedirs(output_dir, exist_ok=True)

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.predictor.set_image(image_rgb)

        mask_paths = []

        for idx, det in enumerate(detections):
            bbox = det["bbox"]
            input_box = np.array(bbox)

            masks, scores, logits = self.predictor.predict(
                box=input_box,
                multimask_output=False
            )

            mask = masks[0].astype(np.uint8) * 255

            mask_filename = os.path.join(output_dir, f"obj_{idx+1:02d}.png")
            cv2.imwrite(mask_filename, mask)

            mask_paths.append(mask_filename)

            print(f"[INFO] Saved mask: {mask_filename}")

        return mask_paths
