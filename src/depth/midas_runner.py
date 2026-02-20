import torch
import cv2
import numpy as np
import os


class MiDaSRunner:
    def __init__(self, model_type="MiDaS_small"):
        """
        model_type:
        - MiDaS_small (fast CPU)
        - DPT_Hybrid (better quality but slower)
        """
        self.device = torch.device("cpu")

        # Load model from torch hub
        self.model = torch.hub.load("intel-isl/MiDaS", model_type)
        self.model.to(self.device)
        self.model.eval()

        # Load transforms
        midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms")

        if model_type == "MiDaS_small":
            self.transform = midas_transforms.small_transform
        else:
            self.transform = midas_transforms.default_transform

        print(f"[INFO] Loaded {model_type} on CPU")

    def run(self, image, output_path):
        """
        image: numpy BGR image (from cv2)
        output_path: where to save depth.png
        """

        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        input_batch = self.transform(img_rgb).to(self.device)

        with torch.no_grad():
            prediction = self.model(input_batch)

            prediction = torch.nn.functional.interpolate(
                prediction.unsqueeze(1),
                size=img_rgb.shape[:2],
                mode="bicubic",
                align_corners=False,
            ).squeeze()

        depth = prediction.cpu().numpy()

        # Normalize depth for visualization
        depth_min = depth.min()
        depth_max = depth.max()

        depth_norm = (depth - depth_min) / (depth_max - depth_min + 1e-8)
        depth_img = (depth_norm * 255).astype(np.uint8)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        cv2.imwrite(output_path, depth_img)

        print(f"[INFO] Depth map saved at {output_path}")

        return depth_img, depth_norm
