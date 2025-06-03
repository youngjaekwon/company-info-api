from typing import AsyncGenerator, Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
    AsyncEngine,
)

from app.core.config import Settings, get_settings


def create_database_engine(
    settings: Annotated[Settings, Depends(get_settings)],
):
    return create_async_engine(
        url=settings.DATABASE_URL,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
        pool_timeout=settings.DATABASE_POOL_TIMEOUT,
        pool_recycle=settings.DATABASE_POOL_RECYCLE,
        echo=settings.SQLALCHEMY_ECHO,
        connect_args={"server_settings": {"search_path": settings.DATABASE_SCHEMA}},
    )


def create_session_factory(
    engine: Annotated[AsyncEngine, Depends(create_database_engine)],
):
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def get_db(
    session_factory: Annotated[async_sessionmaker, Depends(create_session_factory)],
) -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()
