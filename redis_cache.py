import redis

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)
print("Redis connected:", redis_client.ping())