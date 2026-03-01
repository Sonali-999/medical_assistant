# import mysql.connector
# import pyrebase
# import pyrebase
# from db import get_db_connection
# import hashlib 
# firebaseConfig = {
#   "apiKey": "AIzaSyCDD4VWOfdgtXMnqjVQnhJLg_Jlm9psJfM",
#   "authDomain": "medical-assistant-d6b7f.firebaseapp.com",
#   "projectId": "medical-assistant-d6b7f",
#   "storageBucket": "medical-assistant-d6b7f.firebasestorage.app",
#   "messagingSenderId": "338252346051",
#   "appId": "1:338252346051:web:a81fbdefd8df7d43ece876",
#   "measurementId": "G-NN2E1RFNQK",
#   "databaseURL": ""
# }
# firebase = pyrebase.initialize_app(firebaseConfig)
# auth = firebase.auth()

# # MySQL connection
# def get_db():
#     return mysql.connector.connect(
#         host="localhost",
#         user="root",
#         password="yourpassword",
#         database="medical_assistant"
#     )

# # # Register or login with Firebase
# # def firebase_register(email, password):
# #     try:
# #         user = auth.create_user_with_email_and_password(email, password)
# #         firebase_uid = user["localId"]
# #         save_user_to_mysql(firebase_uid, email)
# #         return True, "User registered successfully"
# #     except Exception as e:
# #         return False, str(e)

# # def firebase_login(email, password):
# #     try:
# #         user = auth.sign_in_with_email_and_password(email, password)
# #         firebase_uid = user["localId"]
# #         save_user_to_mysql(firebase_uid, email)  # ensures user exists in MySQL too
# #         return True, firebase_uid
# #     except Exception as e:
# #         return False, str(e)
    
# def register_user(email, password):
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     # optional: hash password
#     hashed_pw = hashlib.sha256(password.encode()).hexdigest()
#     try:
#         cursor.execute(
#             "INSERT INTO users (email, password) VALUES (%s, %s)",
#             (email, hashed_pw)
#         )
#         conn.commit()
#         return "User registered"
#     except Exception as e:
#         return str(e)
#     finally:
#         cursor.close()
#         conn.close()


# def login_user(email, password):
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     hashed_pw = hashlib.sha256(password.encode()).hexdigest()
#     cursor.execute(
#         "SELECT id FROM users WHERE email=%s AND password=%s",
#         (email, hashed_pw)
#     )
#     result = cursor.fetchone()
#     cursor.close()
#     conn.close()
#     if result:
#         return {"status": "success", "user_id": result[0]}
#     else:
#         return {"status": "fail"}

# # Save user to MySQL if not already there
# def save_user_to_mysql(firebase_uid, email):
#     conn = get_db()
#     cursor = conn.cursor()
#     cursor.execute("SELECT id FROM users WHERE firebase_uid=%s", (firebase_uid,))
#     existing = cursor.fetchone()
#     if not existing:
#         cursor.execute("INSERT INTO users (firebase_uid, email) VALUES (%s, %s)",
#                        (firebase_uid, email))
#         conn.commit()
#     cursor.close()
#     conn.close()

# # Save chat
# def save_user_chat(user_id, user_msg, bot_msg):
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute(
#         "INSERT INTO chats (user_id, user_msg, bot_msg) VALUES (%s, %s, %s)",
#         (user_id, user_msg, bot_msg)
#     )
#     conn.commit()
#     cursor.close()
#     conn.close()

# # Get chats
# def get_user_chats(user_id):
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute(
#         "SELECT user_msg, bot_msg FROM chats WHERE user_id=%s ORDER BY id ASC",
#         (user_id,)
#     )
#     results = cursor.fetchall()
#     cursor.close()
#     conn.close()
#     return results



# auth.py
from db import get_db_connection
import hashlib

# Register user
def register_user(email, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    try:
        cursor.execute(
            "INSERT INTO users (email, password) VALUES (%s, %s)",
            (email, hashed_pw)
        )
        conn.commit()
        return "User registered"
    except Exception as e:
        return str(e)
    finally:
        cursor.close()
        conn.close()

# Login user
def login_user(email, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute(
        "SELECT id FROM users WHERE email=%s AND password=%s",
        (email, hashed_pw)
    )
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result:
        return {"status": "success", "user_id": result[0]}
    else:
        return {"status": "fail"}

# Save chat
def save_user_chat(user_id, user_msg, bot_msg):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chats (user_id, user_msg, bot_msg) VALUES (%s, %s, %s)",
        (user_id, user_msg, bot_msg)
    )
    conn.commit()
    cursor.close()
    conn.close()

# Get chats
def get_user_chats(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT user_msg, bot_msg FROM chats WHERE user_id=%s ORDER BY id ASC",
        (user_id,)
    )
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    # Convert from list of tuples → list of lists (for Gradio Chatbot)
    return [[str(u or ""), str(b or "")] for u, b in results]


