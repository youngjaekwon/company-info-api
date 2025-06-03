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
    from app.db import models  # noqa: F401
    from app.db.base import Base

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
    async_session_factory = async_sessionmaker(
        bind=_test_engine, expire_on_commit=False
    )
    async with _test_engine.connect() as conn:
        trans = await conn.begin()
        async with async_session_factory(bind=conn) as session:
            yield session
        await trans.rollback()


@pytest.fixture()
async def redis_client():
    redis_client = await fakeredis.aioredis.FakeRedis()
    yield redis_client
    await redis_client.flushall()
    await redis_client.close()


@pytest.fixture()
def fastapi_client(async_session, redis_client, settings):
    from fastapi.testclient import TestClient

    from app.core.config import get_settings
    from app.db.redis import get_redis_client
    from app.db.session import get_db
    from app.main import create_app

    # 테스트용 앱 생성
    app = create_app()

    # 의존성 오버라이드
    async def override_get_db():
        yield async_session

    def override_get_redis_client():
        return redis_client

    def override_get_settings():
        return settings

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis_client] = override_get_redis_client
    app.dependency_overrides[get_settings] = override_get_settings

    with TestClient(app) as client:
        yield client
