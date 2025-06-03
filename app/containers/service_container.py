from dependency_injector import containers, providers

from app.services.company_service import CompanyService


class ServiceContainer(containers.DeclarativeContainer):
    company_repo = providers.Dependency()
    company_mapper = providers.Dependency()

    company_service = providers.Factory(
        CompanyService,
        company_repo=company_repo,
        company_mapper=company_mapper,
    )
