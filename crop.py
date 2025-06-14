from ultralytics import YOLO 
import cv2
import time

# Load YOLOv8 model
model = YOLO('best.pt')  # Your trained model

# Setup webcam
cap = cv2.VideoCapture(0)

# Required classes and their confidence thresholds
required_classes = {
    'license-card': 0.93,
    'name': 0.50,
    'valid_till': 0.50,
    'dl_number': 0.50
}

detected = set()
license_card_detected = False
cropped_license_card = None  # To store cropped license card

start_time = time.time()
duration = 20  # seconds

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Run detection
    results = model(frame)[0]

    # Loop through detections
    for box in results.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        confidence = float(box.conf[0])
        class_id = int(box.cls[0])
        label = model.names[class_id]

        # Draw bounding box and label
        if confidence > 0.5:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f'{label} {confidence:.2f}', (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Track if required fields are detected
        if label in required_classes:
            if confidence >= required_classes[label]:
                detected.add(label)
                if label == 'license-card' and not license_card_detected:
                    license_card_detected = True
                    # Crop and save the license card
                    cropped_license_card = frame[y1:y2, x1:x2].copy()

    # Show frame
    cv2.imshow('Live Detection', frame)

    # Check time elapsed
    elapsed_time = time.time() - start_time
    if elapsed_time >= duration:
        break

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# After 20 seconds, evaluate result
cv2.destroyAllWindows()
cap.release()

if 'license-card' in detected:
    if all(field in detected for field in required_classes):
        print("✅ Access Granted")
        if cropped_license_card is not None:
            cv2.imshow("Cropped License Card", cropped_license_card)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
    else:
        print("❌ Access Denied - Missing fields")
else:
    print("⏳ No license card detected ❌ Access Denied")
