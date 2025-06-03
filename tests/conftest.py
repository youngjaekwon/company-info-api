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
def fastapi_client(_test_engine, redis_client, settings):
    from dependency_injector import providers
    from fastapi.testclient import TestClient
    from sqlalchemy.ext.asyncio import async_sessionmaker

    from app.containers.main_container import AppContainer
    from app.main import create_app

    # 테스트용 앱 생성
    app = create_app()

    # 테스트용 컨테이너 설정
    container = AppContainer()

    # 테스트 데이터베이스와 Redis 설정
    async_session_maker = async_sessionmaker(bind=_test_engine, expire_on_commit=False)

    container.settings.override(providers.Object(settings))
    container.db.session.override(providers.Factory(async_session_maker))
    container.db.redis_client.override(providers.Object(redis_client))

    app.container = container
    container.wire(modules=["app.api.v1.company"])

    with TestClient(app) as client:
        yield client
