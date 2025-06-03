from dependency_injector import containers, providers

from app.services.company_service import CompanyService


class ServiceContainer(containers.DeclarativeContainer):
    db = providers.Dependency()
    repos = providers.DependenciesContainer()

    company_service = providers.Factory(
        CompanyService,
        db=db,
        company_repo=repos.company_repository,
        company_tag_repo=repos.company_tag_repository,
        company_mapper=repos.company_mapper,
        company_tag_mapper=repos.company_tag_mapper,
    )
