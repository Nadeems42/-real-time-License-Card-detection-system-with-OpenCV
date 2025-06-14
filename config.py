import os

class Config:
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('root', '')
    MYSQL_DB = os.getenv('MYSQL_DB', 'license_db')
    SECRET_KEY = os.getenv('SECRET_KEY', '12345')
    SESSION_TYPE = 'filesystem'
    TEMP_UPLOAD_FOLDER = 'static/temp'