import redis.asyncio as redis

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True,
    max_connections=10
)

async def get_cached_or_search(cache_key, search_fn, ttl=300):

    cached = await redis_client.get(cache_key)
    if cached:
        return f"(cached)\n{cached}"


    result = await search_fn()

    await redis_client.set(cache_key, result, ex=ttl)
    return result