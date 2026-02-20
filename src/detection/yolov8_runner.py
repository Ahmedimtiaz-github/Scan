from ultralytics import YOLO
import os
import json


class YOLOv8Runner:
    def __init__(self, model_name="yolov8n.pt"):
        """
        model_name:
        - yolov8n.pt  (nano, fastest CPU)
        - yolov8s.pt  (small, better accuracy)
        """
        self.model = YOLO(model_name)
        print(f"[INFO] Loaded {model_name}")

    def run(self, image, output_json_path):
        """
        image: numpy BGR image (from cv2)
        output_json_path: where to save detections.json
        """

        results = self.model(image)

        detections = []

        for r in results:
            boxes = r.boxes
            if boxes is None:
                continue

            for box in boxes:
                bbox = box.xyxy[0].tolist()   # [x1, y1, x2, y2]
                cls = int(box.cls[0])
                conf = float(box.conf[0])

                detections.append({
                    "bbox": bbox,
                    "class_id": cls,
                    "confidence": conf
                })

        os.makedirs(os.path.dirname(output_json_path), exist_ok=True)

        with open(output_json_path, "w") as f:
            json.dump(detections, f, indent=4)

        print(f"[INFO] Detections saved at {output_json_path}")

        return detections
