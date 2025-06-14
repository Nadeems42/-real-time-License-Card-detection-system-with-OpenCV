import mysql.connector
from db_config import DB_CONFIG
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    """Create and return a new database connection"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise

def verify_license(dl_number, name, valid_till):
    """
    Check if license exists in database
    Returns tuple of (exists: bool, details: dict)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
        SELECT * FROM licenses 
        WHERE dl_number = %s AND name LIKE %s AND valid_till = %s
        """
        cursor.execute(query, (dl_number, f"%{name}%", valid_till))
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if result:
            return True, {
                'dl_number': result['dl_number'],
                'name': result['name'],
                'valid_till': result['valid_till'],
                'image_path': result['image_path'],
                'created_at': result['created_at']
            }
        return False, None
        
    except Exception as e:
        logger.error(f"License verification error: {e}")
        return False, None

def add_license(dl_number, name, valid_till, image_path):
    """
    Add new license to database
    Returns tuple of (success: bool, message: str)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if license already exists
        check_query = "SELECT id FROM licenses WHERE dl_number = %s"
        cursor.execute(check_query, (dl_number,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return False, "License already exists in database"
        
        # Insert new license
        query = """
        INSERT INTO licenses (dl_number, name, valid_till, image_path, created_at)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (dl_number, name, valid_till, image_path, datetime.now()))
        conn.commit()
        
        cursor.close()
        conn.close()
        return True, "License added successfully"
        
    except Exception as e:
        logger.error(f"License addition error: {e}")
        return False, str(e)

def check_admin_password(password):
    """
    Simple password check (in production, use proper hashing)
    Returns tuple of (valid: bool, message: str)
    """
    # In production, use: from werkzeug.security import check_password_hash
    correct_password = "admin123"  # Change this in production
    if password == correct_password:
        return True, "Password correct"
    return False, "Incorrect password"