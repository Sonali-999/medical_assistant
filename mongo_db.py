from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

client = MongoClient(MONGO_URI)
db = client["medical_assistant"]

users_collection         = db["users"]
chats_collection         = db["chats"]
prescriptions_collection = db["prescriptions"]

# Force-create prescriptions collection if it doesn't exist yet.
# MongoDB is lazy — collections only appear in Compass after first insert.
# create_collection() makes it visible immediately even when empty.
existing = db.list_collection_names()
if "prescriptions" not in existing:
    db.create_collection("prescriptions")
    print("[mongo] Created 'prescriptions' collection")
else:
    print("[mongo] 'prescriptions' collection already exists")