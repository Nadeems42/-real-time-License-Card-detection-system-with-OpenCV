import cv2
import numpy as np
from ultralytics import YOLO
from PIL import Image
import io

# Load models
license_model = YOLO('best.pt')
fields_model = YOLO('best.pt')

def detect_license_card(image):
    """
    Detect license card in image using YOLOv8
    Returns cropped image, confidence, and bounding box coordinates
    """
    results = license_model.predict(image, conf=0.93, classes=[0])
    if len(results[0].boxes) > 0:
        box = results[0].boxes[0]
        confidence = box.conf.item()
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        cropped = image[y1:y2, x1:x2]
        return cropped, confidence, (x1, y1, x2, y2)
    return None, 0, (0, 0, 0, 0)

def detect_license_fields(image):
    """
    Detect fields (name, dl_number, valid_till) in cropped license image
    Returns dictionary with field images and their coordinates
    """
    results = fields_model.predict(image, conf=0.85, classes=[1, 2, 3])
    
    fields = {}
    for box in results[0].boxes:
        cls = int(box.cls.item())
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        
        if cls == 1:
            field_name = 'name'
        elif cls == 2:
            field_name = 'dl_number'
        elif cls == 3:
            field_name = 'valid_till'
        else:
            continue
            
        fields[field_name] = {
            'image': image[y1:y2, x1:x2],
            'coordinates': (x1, y1, x2, y2)
        }
    
    return fields

def bytes_to_cv2image(image_bytes):
    """Convert image bytes to OpenCV format"""
    image = Image.open(io.BytesIO(image_bytes))
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

def draw_detection_box(image, box, confidence):
    """Draw detection box on image"""
    x1, y1, x2, y2 = box
    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.putText(image, f"License: {confidence:.2f}%", (x1, y1-10), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    return image