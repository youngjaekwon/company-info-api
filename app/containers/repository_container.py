from dependency_injector import containers, providers

from app.mappers.company_mapper import CompanyMapper
from app.mappers.company_tag_mapper import CompanyTagMapper
from app.repositories.company_repository import CompanyRepository
from app.repositories.company_tag_repository import CompanyTagRepository


class RepositoryContainer(containers.DeclarativeContainer):
    db = providers.Dependency()
    redis_client = providers.Dependency()
    settings = providers.Dependency()

    # Mappers
    company_mapper = providers.Factory(CompanyMapper)
    company_tag_mapper = providers.Factory(CompanyTagMapper)

    # Repositories
    company_repository = providers.Factory(
        CompanyRepository,
        db=db,
        redis_client=redis_client,
        company_mapper=company_mapper,
        settings=settings,
    )
    company_tag_repository = providers.Factory(
        CompanyTagRepository,
        db=db,
        company_tag_mapper=company_tag_mapper,
    )
