import redis.asyncio as redis

from app.core.config import Settings


def create_redis_pool(settings: Settings):
    return redis.ConnectionPool(
        host=settings.REDIS_URL,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        password=settings.REDIS_PASSWORD,
        decode_responses=True,
        max_connections=settings.REDIS_MAX_CONNECTIONS,
    )


def create_redis_client(redis_pool):
    return redis.Redis(connection_pool=redis_pool)


async def close_redis_client(redis_client):
    await redis_client.close()
