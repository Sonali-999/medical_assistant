from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = "mongodb://localhost:27017"

client = MongoClient(MONGO_URI)
db = client["medical_assistant"]

users_collection = db["users"]
chats_collection = db["chats"]