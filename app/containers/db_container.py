from dependency_injector import containers, providers

from app.db.redis import create_redis_client, create_redis_pool
from app.db.session import create_database_engine, create_session_factory


class DBContainer(containers.DeclarativeContainer):
    settings = providers.Dependency()

    engine = providers.Singleton(
        create_database_engine,
        settings=settings,
    )

    session_factory = providers.Singleton(
        create_session_factory,
        engine=engine,
    )

    session = providers.Factory(
        lambda session_factory: session_factory(),
        session_factory=session_factory,
    )

    redis_pool = providers.Singleton(
        create_redis_pool,
        settings=settings,
    )

    redis = providers.Singleton(
        create_redis_client,
        redis_pool=redis_pool,
    )
