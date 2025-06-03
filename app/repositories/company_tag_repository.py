from sqlalchemy import select, tuple_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import CompanyTagName, CompanyTag
from app.domain.company_entity import CompanyTagEntity
from app.dto.company_dto import CompanyTagNameDto
from app.mappers.company_tag_mapper import CompanyTagMapper


class CompanyTagRepository:
    def __init__(self, db: AsyncSession, company_tag_mapper: CompanyTagMapper):
        self._db = db
        self._company_tag_mapper = company_tag_mapper

    async def get_by_names(
        self, names: list[CompanyTagNameDto]
    ) -> CompanyTagEntity | None:
        expected_match_count = len(names)

        subquery = (
            select(CompanyTagName.company_tag_id)
            .where(
                tuple_(CompanyTagName.language_code, CompanyTagName.name)
                .in_([(name.language_code, name.name) for name in names])
                .group_by(CompanyTagName.company_tag_id)
                .having(func.count() == expected_match_count)
            )
            .subquery()
        )

        stmt = (
            select(CompanyTag)
            .where(CompanyTag.id.in_(select(subquery)))
            .options(selectinload(CompanyTag.names))
        )

        result = await self._db.execute(stmt)
        company_tag_row = result.scalars().first()
        return (
            self._company_tag_mapper.row_to_entity(company_tag_row)
            if company_tag_row
            else None
        )

    async def save_all(self, tags: list[CompanyTagEntity]) -> None:
        tag_rows = [self._company_tag_mapper.entity_to_row(tag) for tag in tags]
        self._db.add_all(tag_rows)
