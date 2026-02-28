# db.py
import mysql.connector

def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="aim_user",        # change if you used another user
        password="Sonali@2005", # the password you set in SQL
        database="medical_assistant"
    )
    return conn
