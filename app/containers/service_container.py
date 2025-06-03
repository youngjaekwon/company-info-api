from dependency_injector import containers, providers

from app.services.company_service import CompanyService


class ServiceContainer(containers.DeclarativeContainer):
    company_service = providers.Factory(
        CompanyService,
        company_repo=providers.Dependency(),
        company_mapper=providers.Dependency(),
    )
