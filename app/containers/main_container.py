from dependency_injector import containers

from app.containers.db_container import DBContainer
from app.containers.repository_container import RepositoryContainer


class AppContainer(containers.DeclarativeContainer):
    db = DBContainer()
    repositories = RepositoryContainer(db=db.session)
