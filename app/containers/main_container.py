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
        db=db.provided.session,
        redis_client=db.provided.redis_client,
        settings=settings,
    )

    services = providers.Container(
        ServiceContainer,
        db=db.provided.session,
        company_repo=repositories.provided.company_repository,
        company_tag_repo=repositories.provided.company_tag_repository,
        company_mapper=repositories.provided.company_mapper,
        company_tag_mapper=repositories.provided.company_tag_mapper,
    )
