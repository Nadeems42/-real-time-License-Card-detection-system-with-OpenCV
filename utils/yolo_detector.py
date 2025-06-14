import torch
from ultralytics import YOLO

# Allow safe globals
torch.serialization.add_safe_globals([torch.nn.Module, 'ultralytics.nn.tasks.DetectionModel'])

# Load YOLOv8 model (ensure the path to your model is correct)
model = YOLO('runs/detect/train5/weights/best.pt')  # Update with your path

def detect_card(frame):
    results = model(frame)  # Inference
    if len(results) > 0 and results[0].boxes:
        box = results[0].boxes[0]  # Get the first detection
        confidence = box.conf[0]  # Confidence score

        if confidence > 0.9:  # Confidence threshold
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()  # Get bounding box coordinates
            cropped_img = frame[int(y1):int(y2), int(x1):int(x2)]  # Crop image
            return cropped_img, confidence
    return None, 0
