from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["medical_assistant"]

print("✅ Connected to MongoDB")

# insert test
db.test.insert_one({"msg": "hello"})

print("✅ Inserted test document")