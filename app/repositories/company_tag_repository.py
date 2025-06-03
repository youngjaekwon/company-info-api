from sqlalchemy import func, select, tuple_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import CompanyTag, CompanyTagName
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
        if not names:
            return None

        stmt = (
            select(CompanyTag, func.count(CompanyTagName.id).label("match_count"))
            .join(CompanyTag.names)
            .where(
                tuple_(CompanyTagName.name, CompanyTagName.language_code).in_(
                    [(name.name, name.language_code) for name in names]
                )
            )
            .group_by(CompanyTag.id)
            .order_by(func.count(CompanyTagName.id).desc())
            .options(selectinload(CompanyTag.names))
            .limit(1)
        )

        result = await self._db.execute(stmt)
        company_tag_row = result.first()
        return (
            self._company_tag_mapper.row_to_entity(company_tag_row[0])
            if company_tag_row
            else None
        )

    async def save(self, tag: CompanyTagEntity) -> CompanyTagEntity:
        tag_row = self._company_tag_mapper.entity_to_row(tag)
        self._db.add(tag_row)
        await self._db.flush()
        await self._db.refresh(tag_row)
        return self._company_tag_mapper.row_to_entity(tag_row)

    async def save_all(self, tags: list[CompanyTagEntity]) -> None:
        tag_rows = [self._company_tag_mapper.entity_to_row(tag) for tag in tags]
        self._db.add_all(tag_rows)

    async def add_missing_names(
        self, tag: CompanyTagEntity, names: list[CompanyTagNameDto]
    ) -> CompanyTagEntity:
        stmt = (
            select(CompanyTag)
            .where(CompanyTag.id == tag.id)
            .options(selectinload(CompanyTag.names))
        )
        result = await self._db.execute(stmt)
        tag_row = result.scalar_one_or_none()
        if not tag_row:
            return tag

        existing_language_codes = {name.language_code for name in tag_row.names}
        created_tag_names = []

        for name in names:
            if not name.language_code or not name.name:
                continue
            if name.language_code in existing_language_codes:
                continue
            created_tag_names.append(
                CompanyTagName(
                    language_code=name.language_code,
                    name=name.name,
                    company_tag_id=tag_row.id,
                )
            )

        self._db.add_all(created_tag_names)
        await self._db.flush()
        await self._db.refresh(tag_row)

        return self._company_tag_mapper.row_to_entity(tag_row)
