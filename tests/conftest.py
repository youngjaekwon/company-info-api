import asyncio

import fakeredis.aioredis
import pytest
from sqlalchemy import StaticPool
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def settings():
    from app.core.config import Settings
    from app.core.constants import EnvConstants, get_env_file

    yield Settings(_env_file=get_env_file(EnvConstants.TEST))


@pytest.fixture(scope="session")
async def _test_engine(settings):
    from app.db.base import Base
    from app.db import models  # noqa: F401

    engine = create_async_engine(
        url=settings.DATABASE_URL,
        future=True,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture()
async def async_session(_test_engine):
    async_session = async_sessionmaker(bind=_test_engine, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.rollback()

@pytest.fixture()
async def redis_client():
    redis_client = await fakeredis.aioredis.FakeRedis()
    yield redis_client
    await redis_client.flushall()
    await redis_client.close()
