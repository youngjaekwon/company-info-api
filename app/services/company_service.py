import logging

from app.dto.company_dto import CompanySearchResultDto
from app.interfaces.company_repository import ICompanyRepository
from app.mappers.company_mapper import CompanyMapper

logger = logging.getLogger(__name__)


class CompanyService:
    def __init__(self, company_repo: ICompanyRepository, company_mapper: CompanyMapper):
        self._company_repo = company_repo
        self._company_mapper = company_mapper

    async def get_by_name(
        self, name: str, language_code: str
    ) -> CompanySearchResultDto | None:
        company = await self._company_repo.get_by_name(name=name)
        if company is None:
            return None

        try:
            return self._company_mapper.entity_to_search_result(company, language_code)
        except ValueError as e:
            logger.warning(
                f"Company with invalid names found: {e}, searched with Company name: {name}"
            )
            return None

    async def get_by_partial_name(
        self, partial_name: str, language_code: str
    ) -> list[CompanySearchResultDto]:
        companies = await self._company_repo.get_by_partial_name(
            partial_name=partial_name
        )

        result = []
        for company in companies:
            try:
                result.append(
                    self._company_mapper.dto_to_search_result(company, language_code)
                )
            except ValueError as e:
                logger.warning(
                    f"Company with invalid names found: {e}, searched with partial name: {partial_name}"
                )
                continue
        return result

    async def get_by_tag(
        self, tag: str, language_code: str
    ) -> list[CompanySearchResultDto]:
        companies = await self._company_repo.get_by_tag(tag=tag)

        result = []
        for company in companies:
            try:
                result.append(
                    self._company_mapper.dto_to_search_result(company, language_code)
                )
            except ValueError as e:
                logger.warning(
                    f"Company with invalid names found: {e}, searched with tag: {tag}"
                )
                continue
        return result
