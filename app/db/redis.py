from typing import Annotated

import redis.asyncio as redis
from fastapi import Depends

from app.core.config import Settings, get_settings


def create_redis_pool(settings: Annotated[Settings, Depends(get_settings)]):
    return redis.ConnectionPool(
        host=settings.REDIS_URL,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        password=settings.REDIS_PASSWORD,
        decode_responses=True,
        max_connections=settings.REDIS_MAX_CONNECTIONS,
    )


async def get_redis_client(
    redis_pool: Annotated[redis.ConnectionPool, Depends(create_redis_pool)],
):
    redis_client = redis.Redis(connection_pool=redis_pool)
    try:
        yield redis_client
    finally:
        await redis_client.aclose()


async def close_redis_client(
    redis_client: Annotated[redis.Redis, Depends(get_redis_client)],
):
    await redis_client.close()
