import cv2
import numpy as np
from paddleocr import PaddleOCR
import pytesseract
import re
from datetime import datetime

# Initialize PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)

def preprocess_image(image):
    """Preprocess image for better OCR results"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(gray, 255, 
                                 cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                 cv2.THRESH_BINARY, 11, 2)
    
    # Apply slight blur to reduce noise
    blurred = cv2.GaussianBlur(thresh, (1, 1), 0)
    
    return blurred

def extract_text_from_image(image):
    """
    Extract text from image using PaddleOCR with fallback to Tesseract
    Returns cleaned and formatted text
    """
    # Preprocess image
    processed_img = preprocess_image(image)
    
    # Try PaddleOCR first
    result = ocr.ocr(processed_img, cls=True)
    text = ''
    
    if result and len(result) > 0 and result[0] is not None:
        # Combine all detected text with confidence > 0.7
        text = ' '.join([line[1][0] for line in result[0] if line[1][1] > 0.7])
    else:
        # Fallback to Tesseract
        text = pytesseract.image_to_string(processed_img, config='--psm 6')
    
    # Clean and format the text
    cleaned_text = clean_extracted_text(text)
    return cleaned_text

def clean_extracted_text(text):
    """Clean and format extracted text"""
    # Remove special characters except spaces, letters, numbers and basic punctuation
    cleaned = re.sub(r'[^\w\s\-/]', '', text.strip())
    
    # Replace multiple spaces with single space
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    # Format dates if detected
    date_formats = [
        r'\d{2}/\d{2}/\d{4}',
        r'\d{2}-\d{2}-\d{4}',
        r'\d{4}-\d{2}-\d{2}'
    ]
    
    for fmt in date_formats:
        dates = re.findall(fmt, cleaned)
        for date in dates:
            try:
                # Standardize date format to YYYY-MM-DD
                parsed = datetime.strptime(date, '%d/%m/%Y')
                standardized = parsed.strftime('%Y-%m-%d')
                cleaned = cleaned.replace(date, standardized)
            except:
                try:
                    parsed = datetime.strptime(date, '%d-%m-%Y')
                    standardized = parsed.strftime('%Y-%m-%d')
                    cleaned = cleaned.replace(date, standardized)
                except:
                    pass
    
    return cleaned