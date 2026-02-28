
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
# Save chat (unchanged)
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


# Get chats - return dicts for Gradio Chatbot directly
def get_user_chats(user_id):
    """
    Fetch full chat history for a user including:
    id, user_id, user_msg, bot_msg, created_at
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # returns dict for easy access
    cursor.execute(
        "SELECT id, user_id, user_msg, bot_msg, created_at "
        "FROM chats WHERE user_id=%s ORDER BY created_at ASC",
        (user_id,)
    )
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    # Print nicely for debug
    for chat in results:
        print(f"Chat ID: {chat['id']}")
        print(f"User ID: {chat['user_id']}")
        print(f"User Msg: {chat['user_msg']}")
        print(f"Bot Msg: {chat['bot_msg']}")
        print(f"Timestamp: {chat['created_at']}")
        print("-" * 40)

    return results