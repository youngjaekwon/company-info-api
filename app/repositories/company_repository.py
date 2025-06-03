from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Company, CompanyName, CompanyTag, CompanyTagName
from app.domain.company_entity import CompanyEntity
from app.dto.company_dto import CompanyDto
from app.mappers.company_mapper import CompanyMapper


class CompanyRepository:
    def __init__(self, db: AsyncSession, company_mapper: CompanyMapper):
        self._db = db
        self._company_mapper = company_mapper

    async def get_by_name(self, name: str) -> CompanyEntity | None:
        stmt = (
            select(Company)
            .join(Company.names)
            .where(CompanyName.name == name)
            .options(
                selectinload(Company.names),
                selectinload(Company.tags).selectinload(CompanyTag.names),
            )
        )
        result = await self._db.execute(stmt)
        company = result.scalars().first()
        return self._company_mapper.row_to_entity(company) if company else None

    async def get_by_partial_name(self, partial_name: str) -> list[CompanyDto]:
        stmt = (
            select(Company)
            .join(Company.names)
            .where(
                CompanyName.name.ilike(f"%{partial_name}%"),
            )
            .options(selectinload(Company.names))
        )
        result = await self._db.execute(stmt)
        companies = result.scalars().all()
        return [
            self._company_mapper.row_to_search_result_dto(company)
            for company in companies
        ]

    async def get_by_tag(self, tag: str) -> list[CompanyDto]:
        stmt = (
            select(Company)
            .join(Company.tags)
            .join(CompanyTag.names)
            .where(CompanyTagName.name == tag)
            .options(selectinload(Company.names))
        )
        result = await self._db.execute(stmt)
        companies = result.scalars().all()
        return [
            self._company_mapper.row_to_search_result_dto(company)
            for company in companies
        ]
