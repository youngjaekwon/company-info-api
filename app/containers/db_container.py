from dependency_injector import containers, providers

from app.db.session import AsyncSessionLocal


class DBContainer(containers.DeclarativeContainer):
    session = providers.Factory(AsyncSessionLocal)
