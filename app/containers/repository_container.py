from dependency_injector import containers, providers

from app.mappers.company_mapper import CompanyMapper
from app.repositories.company_repository import CompanyRepository


class RepositoryContainer(containers.DeclarativeContainer):
    db = providers.Dependency()
    redis_client = providers.Dependency()
    settings = providers.Dependency()

    # Mappers
    company_mapper = providers.Factory(CompanyMapper)

    # Repositories
    company_repository = providers.Factory(
        CompanyRepository,
        db=db,
        redis_client=redis_client,
        company_mapper=company_mapper,
        settings=settings,
    )
