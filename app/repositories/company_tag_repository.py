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

        expected_match_count = len(names)

        # 1단계: 제공된 이름들과 일치하는 company_tag_id들을 찾기
        # (제공된 이름 개수만큼 매치되는 태그들)
        matching_tags_subquery = (
            select(CompanyTagName.company_tag_id)
            .where(
                tuple_(CompanyTagName.language_code, CompanyTagName.name).in_(
                    [(name.language_code, name.name) for name in names]
                )
            )
            .group_by(CompanyTagName.company_tag_id)
            .having(func.count() == expected_match_count)
            .subquery()
        )

        # 2단계: 해당 태그들이 정확히 제공된 이름 개수만큼만 가지고 있는지 확인
        # (추가 이름이 없는지 확인)
        exact_match_subquery = (
            select(CompanyTagName.company_tag_id)
            .where(CompanyTagName.company_tag_id.in_(select(matching_tags_subquery)))
            .group_by(CompanyTagName.company_tag_id)
            .having(func.count() == expected_match_count)
            .subquery()
        )

        stmt = (
            select(CompanyTag)
            .where(CompanyTag.id.in_(select(exact_match_subquery)))
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
