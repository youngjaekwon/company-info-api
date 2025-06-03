from dependency_injector import containers, providers

from app.containers.db_container import DBContainer
from app.containers.repository_container import RepositoryContainer
from app.containers.service_container import ServiceContainer
from app.core.config import Settings


class AppContainer(containers.DeclarativeContainer):
    settings = providers.Singleton(Settings)

    db = providers.Container(
        DBContainer,
        settings=settings,
    )

    repositories = providers.Container(
        RepositoryContainer,
        db=db.session,
        redis_client=db.redis_client,
        settings=settings,
    )

    services = providers.Container(
        ServiceContainer,
        db=db.session,
        repos=repositories,
    )
