import hashlib
from mongo_db import users_collection

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(email, password):
    existing = users_collection.find_one({"email": email})
    if existing:
        return "User already exists"

    users_collection.insert_one({
        "email": email,
        "password": hash_password(password)
    })

    return "User registered successfully"

def login_user(email, password):
    user = users_collection.find_one({"email": email})

    if not user:
        return {"status": "error"}

    if user["password"] != hash_password(password):
        return {"status": "error"}

    return {
        "status": "success",
        "user_id": str(user["_id"])
    }