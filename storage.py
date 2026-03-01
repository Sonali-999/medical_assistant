# storage.py
from firebase_admin import firestore

db = firestore.client()

def save_user_chat(user_id, role, message):
    """Store each message under user -> messages subcollection"""
    doc_ref = db.collection("chats").document(user_id).collection("messages").document()
    doc_ref.set({
        "role": role,
        "message": message,
        "timestamp": firestore.SERVER_TIMESTAMP
    })

def get_user_chats(user_id):
    """Fetch all chats for a user in timestamp order"""
    chats_ref = db.collection("chats").document(user_id).collection("messages").order_by("timestamp")
    results = chats_ref.stream()
    return [{"role": doc.to_dict()["role"], "message": doc.to_dict()["message"]} for doc in results]
