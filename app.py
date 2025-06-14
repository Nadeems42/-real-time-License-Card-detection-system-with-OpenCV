from flask import Flask, render_template, request, redirect, url_for, session, jsonify, Response
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from image_utils import detect_license_card, detect_license_fields, bytes_to_cv2image, draw_detection_box
from ocr_utils import extract_text_from_image
from db_utils import verify_license, add_license, check_admin_password
import cv2
import numpy as np
import time
import logging
from threading import Lock

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'dev-secret-key-123'  # Use env var in production
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Globals
camera_lock = Lock()
camera = None
last_detection_time = 0
DETECTION_COOLDOWN = 2  # seconds

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming with real-time detection"""
    def generate():
        global camera, last_detection_time

        with camera_lock:
            if camera is None:
                camera = cv2.VideoCapture(0)
                camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        while True:
            success, frame = camera.read()
            if not success:
                break

            current_time = time.time()
            processed_frame = frame.copy()

            if current_time - last_detection_time > DETECTION_COOLDOWN:
                try:
                    cropped_img, confidence, box = detect_license_card(frame)
                    if cropped_img is not None and confidence > 0.93:
                        last_detection_time = current_time
                        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                        cropped_filename = f"cropped_{timestamp}.jpg"
                        cropped_path = os.path.join(app.config['UPLOAD_FOLDER'], cropped_filename)
                        cv2.imwrite(cropped_path, cropped_img)
                        session['cropped_image'] = cropped_path
                        processed_frame = draw_detection_box(processed_frame, box, confidence)
                except Exception as e:
                    logger.error(f"Detection error: {e}")

            ret, buffer = cv2.imencode('.jpg', processed_frame)
            frame_bytes = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/detect', methods=['GET', 'POST'])
def detect():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'status': 'error', 'message': 'No file part'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'status': 'error', 'message': 'No selected file'}), 400

        if file and allowed_file(file.filename):
            try:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                img = cv2.imread(filepath)
                cropped_img, confidence, _ = detect_license_card(img)

                if cropped_img is not None and confidence > 0.93:
                    cropped_filename = f"cropped_{filename}"
                    cropped_path = os.path.join(app.config['UPLOAD_FOLDER'], cropped_filename)
                    cv2.imwrite(cropped_path, cropped_img)
                    session['cropped_image'] = cropped_path

                    return jsonify({
                        'status': 'success',
                        'cropped_image': url_for('static', filename=f'uploads/{cropped_filename}'),
                        'confidence': float(confidence)
                    })
                else:
                    return jsonify({'status': 'error', 'message': 'Low confidence'}), 400

            except Exception as e:
                logger.error(f"Image processing error: {e}")
                return jsonify({'status': 'error', 'message': 'Processing failed'}), 500

    return render_template('detect.html')

@app.route('/detect_frame', methods=['POST'])
def detect_frame():
    if 'frame' not in request.files:
        return jsonify({'status': 'error', 'message': 'No frame provided'}), 400

    try:
        frame = request.files['frame']
        img = bytes_to_cv2image(frame.read())

        cropped_img, confidence, box = detect_license_card(img)
        if cropped_img is not None and confidence > 0.93:
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            cropped_filename = f"cropped_{timestamp}.jpg"
            cropped_path = os.path.join(app.config['UPLOAD_FOLDER'], cropped_filename)
            cv2.imwrite(cropped_path, cropped_img)

            return jsonify({
                'status': 'success',
                'detected': True,
                'confidence': float(confidence),
                'cropped_image': url_for('static', filename=f'uploads/{cropped_filename}'),
                'image_path': cropped_path
            })

        return jsonify({'status': 'success', 'detected': False})

    except Exception as e:
        logger.error(f"Frame detection error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if 'cropped_image' not in session:
        return redirect(url_for('detect'))

    cropped_path = session['cropped_image']

    if request.method == 'POST':
        try:
            img = cv2.imread(cropped_path)
            fields = detect_license_fields(img)

            license_data = {}
            for field_name, field_info in fields.items():
                text = extract_text_from_image(field_info['image'])
                license_data[field_name] = text

            valid_till = license_data.get('valid_till', '')
            is_valid = True
            try:
                valid_date = datetime.strptime(valid_till, '%Y-%m-%d').date()
                if valid_date < datetime.now().date():
                    is_valid = False
            except:
                is_valid = False

            exists_in_db, db_details = verify_license(
                license_data.get('dl_number', ''),
                license_data.get('name', ''),
                valid_till
            )

            session['license_data'] = license_data
            session['is_valid'] = is_valid
            session['exists_in_db'] = exists_in_db
            session['db_details'] = db_details

            return jsonify({
                'status': 'success',
                'license_data': license_data,
                'is_valid': is_valid,
                'exists_in_db': exists_in_db
            })

        except Exception as e:
            logger.error(f"Verification error: {e}")
            return jsonify({'status': 'error', 'message': 'Verification failed'}), 500

    return render_template('verify.html', cropped_image=os.path.basename(cropped_path))

@app.route('/result')
def result():
    if 'license_data' not in session:
        return redirect(url_for('home'))

    license_data = session['license_data']
    is_valid = session.get('is_valid', False)
    exists_in_db = session.get('exists_in_db', False)
    db_details = session.get('db_details', {})

    result_type = 'denied'
    if exists_in_db and is_valid:
        result_type = 'success'
    elif not is_valid:
        result_type = 'expired'

    return render_template('result.html',
                           license_data=license_data,
                           is_valid=is_valid,
                           exists_in_db=exists_in_db,
                           db_details=db_details,
                           result_type=result_type)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        password = request.form.get('password')
        valid, message = check_admin_password(password)

        if valid:
            license_data = session.get('license_data', {})
            cropped_path = session.get('cropped_image', '')

            if license_data and cropped_path:
                success, db_message = add_license(
                    license_data.get('dl_number', ''),
                    license_data.get('name', ''),
                    license_data.get('valid_till', ''),
                    cropped_path
                )

                if success:
                    session['exists_in_db'] = True
                    return jsonify({'status': 'success'})

                return jsonify({'status': 'error', 'message': db_message}), 400

        return jsonify({'status': 'error', 'message': message}), 401

    return render_template('admin.html')

@app.teardown_appcontext
def teardown_camera(exception):
    global camera
    with camera_lock:
        if camera is not None:
            camera.release()
            camera = None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

if __name__ == '__main__':
    app.run(debug=True)
