from dependency_injector import containers, providers

from app.services.company_service import CompanyService


class ServiceContainer(containers.DeclarativeContainer):
    db = providers.Dependency()

    company_repo = providers.Dependency()
    company_tag_repo = providers.Dependency()

    company_mapper = providers.Dependency()
    company_tag_mapper = providers.Dependency()

    company_service = providers.Factory(
        CompanyService,
        db=db,
        company_repo=company_repo,
        company_tag_repo=company_tag_repo,
        company_mapper=company_mapper,
        company_tag_mapper=company_tag_mapper,
    )
