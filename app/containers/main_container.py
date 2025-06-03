from dependency_injector import containers, providers

from app.containers.db_container import DBContainer
from app.containers.repository_container import RepositoryContainer
from app.containers.service_container import ServiceContainer


class AppContainer(containers.DeclarativeContainer):
    db = providers.Container(DBContainer)

    repositories = providers.Container(
        RepositoryContainer,
        db=db.provided.session,
    )

    services = providers.Container(
        ServiceContainer,
        company_repo=repositories.provided.company_repository,
        company_mapper=repositories.provided.company_mapper,
    )
