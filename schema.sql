import mysql.connector

def create_database_and_tables():
    conn = mysql.connector.connect(
        host="localhost",
        user="aim_user",        # change if needed
        password="Sonali@2005"  # your MySQL password
    )
    cursor = conn.cursor()
    
    # Create database if not exists
    cursor.execute("""
        CREATE DATABASE IF NOT EXISTS medical_assistant
        CHARACTER SET = utf8mb4
        COLLATE = utf8mb4_unicode_ci;
    """)
    
    # Use the database
    cursor.execute("USE medical_assistant;")
    
    # Drop tables if needed (optional)
    cursor.execute("DROP TABLE IF EXISTS chats;")
    cursor.execute("DROP TABLE IF EXISTS users;")
    
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Create chats table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            user_msg TEXT NOT NULL,
            bot_msg TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Database and tables are ready!")

# Simple helper to get connection to the DB
def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="aim_user",
        password="Sonali@2005",
        database="medical_assistant"
    )
    return conn

# If run as script, create DB and tables
if __name__ == "__main__":
    create_database_and_tables()
