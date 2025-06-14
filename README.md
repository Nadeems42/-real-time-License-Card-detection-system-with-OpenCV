# 🚗 Real-Time License Card Detection System using YOLOv8 and OpenCV

A complete real-time system for detecting and verifying license cards using computer vision, OCR, and secure admin authorization. Built with Flask, YOLOv8, OpenCV, and SQLite.

---

## 📌 Features

- 🔍 YOLOv8-Based Detection: Real-time object detection of license cards via webcam.
- ✂️ Smart Cropping: Automatically crops cards with confidence > 90%.
- 📄 OCR Integration: Extracts license number, name, and expiry date.
- 🔐 Admin Verification: Secure admin-only authorization to approve/save data (password hashed).
- 🧠 Face Verification: Ensures user identity with live face comparison.
- 🗃️ SQLite Database: Stores license data with captured image path.
- 🎨 Modern UI: Clean animated HTML/CSS frontend with verification feedback.

---

## 📁 Project Structure

license_card_detection/
│
├── static/
│   ├── css/
│   └── captured_cards/
│
├── templates/
│   ├── index.html
│   ├── verify.html
│   └── result.html
│
├── utils/
│   ├── image_utils.py
│   ├── ocr_utils.py
│   └── db_utils.py
│
├── best.pt                # Trained YOLOv8 model
├── app.py                 # Main Flask application
├── requirements.txt       # Dependencies
└── README.md

---

## 🚀 How to Run

### 1. Clone the Repository

git clone https://github.com/Nadeems42/-real-time-License-Card-detection-system-with-OpenCV.git
cd -real-time-License-Card-detection-system-with-OpenCV

### 2. Create Virtual Environment (optional)

python -m venv venv
venv\Scripts\activate     # On Windows
source venv/bin/activate  # On macOS/Linux

### 3. Install Dependencies

pip install -r requirements.txt

### 4. Run the Application

python app.py

Open http://127.0.0.1:5000 in your browser.

---

## 🔐 Admin Access

- Only admin can verify and approve license data to be saved into the database.
- Passwords are hashed for security.
- You can change admin credentials in `db_utils.py`.

---

## 🔮 Future Enhancements

- 🔁 Add retry and fail-safe options if OCR fails.
- 🌐 Deploy the app to a public web server.
- 📸 Add automatic photo logging of each verification attempt.
- 🤖 Integrate face verification with deep learning-based face match.

---

## 🤝 Contributing

Want to improve the system? Feel free to fork the repo, create a feature branch, and submit a pull request.

---

## 📜 License

This project is licensed under the MIT License.

---

## 🙋‍♂️ Developed By

**Nathimulla S**  
📍 Chennai, India  
📧 nathimnads786@gmail.com  
📞 +91 7092680975
