from dependency_injector import containers

from app.containers.db_container import DBContainer


class AppContainer(containers.DeclarativeContainer):
    db = DBContainer()
