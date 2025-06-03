from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from redis.asyncio import Redis

from app.core.config import Settings
from app.db.models import Company, CompanyName, CompanyTag, CompanyTagName
from app.domain.company_entity import CompanyEntity
from app.dto.company_dto import CompanyDto
from app.mappers.company_mapper import CompanyMapper


class CompanyRepository:
    _cache_namespace = "repository:company"

    def __init__(
        self,
        db: AsyncSession,
        redis_client: Redis,
        company_mapper: CompanyMapper,
        settings: Settings,
    ):
        self._db = db
        self._redis = redis_client
        self._company_mapper = company_mapper
        self._settings = settings

    async def get_by_name(self, name: str) -> CompanyEntity | None:
        cache_key = f"{self._cache_namespace}:name:{name}"
        if cached := await self._redis.get(cache_key):
            return self._company_mapper.json_to_entity(cached)

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
        if company is None:
            return None

        company_entity = self._company_mapper.row_to_entity(company)
        await self._redis.set(
            cache_key,
            self._company_mapper.entity_to_json(company_entity),
            ex=self._settings.REPOSITORY_CACHE_TTL,
        )

        return company_entity

    async def get_by_partial_name(self, partial_name: str) -> list[CompanyDto]:
        cache_key = f"{self._cache_namespace}:partial_name:{partial_name}"
        if cached := await self._redis.get(cache_key):
            return self._company_mapper.json_to_dtos(cached)

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

        company_dtos = [
            self._company_mapper.row_to_search_result_dto(company)
            for company in companies
        ]
        await self._redis.set(
            cache_key,
            self._company_mapper.dtos_to_json(company_dtos),
            ex=self._settings.REPOSITORY_CACHE_PARTIAL_TTL,  # 부분 검색 특성상 무효화 불가로 짧은 TTL 설정
        )
        return company_dtos

    async def get_by_tag(self, tag: str) -> list[CompanyDto]:
        cache_key = f"{self._cache_namespace}:tag:{tag}"
        if cached := await self._redis.get(cache_key):
            return self._company_mapper.json_to_dtos(cached)

        stmt = (
            select(Company)
            .join(Company.tags)
            .join(CompanyTag.names)
            .where(CompanyTagName.name == tag)
            .options(selectinload(Company.names))
        )
        result = await self._db.execute(stmt)
        companies = result.scalars().all()

        company_dtos = [
            self._company_mapper.row_to_search_result_dto(company)
            for company in companies
        ]
        await self._redis.set(
            cache_key,
            self._company_mapper.dtos_to_json(company_dtos),
            ex=self._settings.REPOSITORY_CACHE_TTL,
        )
        return company_dtos
