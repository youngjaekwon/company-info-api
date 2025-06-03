import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.dto.company_dto import CompanyDto, CompanySearchResultDto, CompanyTagDto
from app.interfaces.company_repository import ICompanyRepository
from app.interfaces.company_tag_repository import ICompanyTagRepository
from app.mappers.company_mapper import CompanyMapper
from app.mappers.company_tag_mapper import CompanyTagMapper

logger = logging.getLogger(__name__)


class CompanyService:
    def __init__(
        self,
        db: AsyncSession,
        company_repo: ICompanyRepository,
        company_tag_repo: ICompanyTagRepository,
        company_mapper: CompanyMapper,
        company_tag_mapper: CompanyTagMapper,
    ):
        self._db = db
        self._company_repo = company_repo
        self._company_tag_repo = company_tag_repo
        self._company_mapper = company_mapper
        self._company_tag_mapper = company_tag_mapper

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

    async def create(
        self, company: CompanyDto, language_code: str
    ) -> CompanySearchResultDto:
        async with self._db.begin():
            tag_entities = []
            for tag in company.tags:
                tag_entity = await self._company_tag_repo.get_by_names(
                    names=list(tag.names)
                )
                if tag_entity is None:
                    new_tag_entity = self._company_tag_mapper.dto_to_entity(tag)
                    tag_entity = await self._company_tag_repo.save(new_tag_entity)
                else:
                    tag_entity = await self._company_tag_repo.add_missing_names(
                        tag=tag_entity, names=list(tag.names)
                    )

                tag_entities.append(tag_entity)

            company_entity = self._company_mapper.dto_to_entity(
                company, tags=tag_entities
            )

            await self._company_repo.save(company=company_entity)

        return self._company_mapper.entity_to_search_result(
            entity=company_entity, language_code=language_code
        )

    async def add_tags(
        self, name: str, tags: list[CompanyTagDto], language_code: str
    ) -> CompanySearchResultDto | None:
        async with self._db.begin():
            tag_entities = []
            for tag in tags:
                tag_entity = await self._company_tag_repo.get_by_names(
                    names=list(tag.names)
                )
                if tag_entity is None:
                    new_tag_entity = self._company_tag_mapper.dto_to_entity(tag)
                    tag_entity = await self._company_tag_repo.save(new_tag_entity)
                else:
                    tag_entity = await self._company_tag_repo.add_missing_names(
                        tag=tag_entity, names=list(tag.names)
                    )

                tag_entities.append(tag_entity)

            company_entity = await self._company_repo.add_tag(
                name=name, tags=tag_entities
            )

        if company_entity is None:
            return None

        return self._company_mapper.entity_to_search_result(
            entity=company_entity, language_code=language_code
        )

    async def remove_tag(
        self, name: str, tag: str, language_code: str
    ) -> CompanySearchResultDto | None:
        async with self._db.begin():
            company_entity = await self._company_repo.remove_tag(name=name, tag=tag)

        if company_entity is None:
            return None

        return self._company_mapper.entity_to_search_result(
            entity=company_entity, language_code=language_code
        )
