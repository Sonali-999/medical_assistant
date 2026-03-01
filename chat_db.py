from mongo_db import chats_collection
from redis_cache import redis_client
import json

# Save chat
def save_user_chat(user_id, user_msg, bot_msg):
    chat = {
        "user_id": user_id,
        "user_msg": user_msg,
        "bot_msg": bot_msg
    }

    # Save in MongoDB
    chats_collection.insert_one(chat)

    # Save in Redis (latest chats cache)
    redis_client.lpush(f"chat:{user_id}", json.dumps(chat))
    redis_client.ltrim(f"chat:{user_id}", 0, 9)  # keep last 10

    return True


# Get chats
def get_user_chats(user_id):
    cached = redis_client.lrange(f"chat:{user_id}", 0, -1)

    if cached:
        print(" FROM REDIS")
        return [json.loads(c) for c in cached]
    print(" FROM MONGO")
    # fallback to MongoDB
    chats = list(chats_collection.find({"user_id": user_id}))

    formatted = []
    for chat in chats:
        formatted.append({
            "user_msg": chat["user_msg"],
            "bot_msg": chat["bot_msg"]
        })

    return formatted