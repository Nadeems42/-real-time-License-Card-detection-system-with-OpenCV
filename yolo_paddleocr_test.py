import cv2
from ultralytics import YOLO
from paddleocr import PaddleOCR
from datetime import datetime
import re

# Classes as per your trained model
classes = ['license_card', 'dl_number', 'name', 'valid_till']

# Load model
model = YOLO('best.pt')

# Load image
image_path = 'sample_license.jpg'
img = cv2.imread(image_path)

# Run detection
results = model(image_path)
boxes = results[0].boxes.xyxy.cpu().numpy()
class_ids = results[0].boxes.cls.cpu().numpy().astype(int)

# Check if anything was detected
if len(boxes) == 0:
    print("❌ No license card detected.")
    exit()

print("✅ License card detected!")

# Setup OCR
ocr = PaddleOCR(use_angle_cls=True, lang='en')

# Store extracted info
extracted_info = {}

for i, box in enumerate(boxes):
    cls_id = class_ids[i]
    if cls_id == 0:
        continue  # Skip full card detection

    label = classes[cls_id]
    x1, y1, x2, y2 = map(int, box[:4])
    roi = img[y1:y2, x1:x2]

    crop_filename = f"crop_{label}.jpg"
    cv2.imwrite(crop_filename, roi)

    ocr_result = ocr.ocr(crop_filename, cls=True)
    extracted_text = ""

    if ocr_result and len(ocr_result[0]) > 0:
        for line in ocr_result[0]:
            extracted_text += line[1][0] + " "
        extracted_text = extracted_text.strip()

        # Clean based on label using regex
        if label == "dl_number":
            match = re.search(r'(TN\d{13})', extracted_text)
            extracted_text = match.group(1) if match else "❌ Not found"
        elif label == "name":
            match = re.search(r'Name\s*[:\-]?\s*([A-Z\s]+)', extracted_text, re.IGNORECASE)
            extracted_text = match.group(1).strip() if match else "❌ Not found"
        elif label == "valid_till":
            match = re.search(r'(\d{2}[-/]\d{2}[-/]\d{4})', extracted_text)
            extracted_text = match.group(1) if match else "❌ Not found"
    else:
        extracted_text = "❌ Not found"

    extracted_info[label] = extracted_text

# Check expiry
valid_till_str = extracted_info.get('valid_till', "❌ Not found")
if valid_till_str != "❌ Not found":
    try:
        valid_date = datetime.strptime(valid_till_str, "%d-%m-%Y")
        today = datetime.today()
        expiry_status = "✅ Valid" if valid_date >= today else "❌ Expired"
    except:
        expiry_status = "❓ Date format invalid"
else:
    expiry_status = "❌ Not found"

# Final output
print("\nFinal Extracted Info:")
print(f"dl_number: {extracted_info.get('dl_number', '❌ Not found')}")
print(f"name: {extracted_info.get('name', '❌ Not found')}")
print(f"valid_till: {valid_till_str} ({expiry_status})")
