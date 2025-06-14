from db_utils import create_connection

def init_db():
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS licenses (
        id INT AUTO_INCREMENT PRIMARY KEY,
        dl_number VARCHAR(255) UNIQUE,
        name VARCHAR(255),
        valid_till DATE,
        image_path VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    print("Database initialized successfully!")
    conn.close()

if __name__ == '__main__':
    init_db()