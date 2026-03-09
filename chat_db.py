from mongo_db import chats_collection
from redis_cache import redis_client
from bson import ObjectId
import json


# ---------------- SAVE CHAT ----------------
def save_user_chat(user_id, user_msg, bot_msg):

    chat = {
        "user_id": str(user_id),   # ensure string
        "user_msg": user_msg,
        "bot_msg": bot_msg
    }

    # Save in MongoDB
    result = chats_collection.insert_one(chat)

    # Convert Mongo ObjectId to string for Redis caching
    chat["_id"] = str(result.inserted_id)

    # Save in Redis cache (latest 10 chats)
    redis_client.lpush(f"chat:{user_id}", json.dumps(chat))
    redis_client.ltrim(f"chat:{user_id}", 0, 9)

    return True


# ---------------- GET CHAT HISTORY ----------------
def get_user_chats(user_id):

    # First check Redis cache
    cached = redis_client.lrange(f"chat:{user_id}", 0, -1)

    if cached:
        print(" FROM REDIS")
        return [json.loads(c) for c in cached]

    print(" FROM MONGO")

    # fallback to MongoDB
    chats = list(chats_collection.find({"user_id": str(user_id)}))

    formatted = []

    for chat in chats:

        formatted.append({
            "_id": str(chat["_id"]),   # convert ObjectId safely
            "user_msg": chat["user_msg"],
            "bot_msg": chat["bot_msg"]
        })

    return formatted