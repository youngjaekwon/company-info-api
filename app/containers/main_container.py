from dependency_injector import containers

from app.containers.db_container import DBContainer
from app.containers.repository_container import RepositoryContainer
from app.containers.service_container import ServiceContainer


class AppContainer(containers.DeclarativeContainer):
    db = DBContainer()
    repositories = RepositoryContainer(db=db.session)
    services = ServiceContainer(
        company_repo=repositories.company_repository,
        company_mapper=repositories.company_mapper,
    )
