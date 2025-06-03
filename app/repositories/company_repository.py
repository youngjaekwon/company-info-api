from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import Settings
from app.db.models import Company, CompanyName, CompanyTag, CompanyTagName
from app.domain.company_entity import CompanyEntity, CompanyTagEntity
from app.dto.company_dto import CompanyDto
from app.mappers.company_mapper import CompanyMapper
from app.mappers.company_tag_mapper import CompanyTagMapper


class CompanyRepository:
    _cache_namespace = "repository:company"

    def __init__(
        self,
        db: AsyncSession,
        redis_client: Redis,
        company_mapper: CompanyMapper,
        company_tag_mapper: CompanyTagMapper,
        settings: Settings,
    ):
        self._db = db
        self._redis = redis_client
        self._company_mapper = company_mapper
        self._company_tag_mapper = company_tag_mapper
        self._settings = settings

    async def _get_by_name(self, name: str) -> Company | None:
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
        return result.scalars().first()

    async def get_by_name(self, name: str) -> CompanyEntity | None:
        cache_key = f"{self._cache_namespace}:name:{name}"
        if cached := await self._redis.get(cache_key):
            return self._company_mapper.json_to_entity(cached)

        company = await self._get_by_name(name)
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

    async def save(self, company: CompanyEntity) -> None:
        company_row = self._company_mapper.entity_to_row(company)

        existing_tag_ids = [tag.id for tag in company.tags if tag.id is not None]

        existing_tags = []
        if existing_tag_ids:
            stmt = (
                select(CompanyTag)
                .where(CompanyTag.id.in_(existing_tag_ids))
                .options(selectinload(CompanyTag.names))
            )
            result = await self._db.execute(stmt)
            existing_tags = list(result.scalars().all())

        new_tags = []
        existing_tag_ids_set = {tag.id for tag in existing_tags}

        for tag_entity in company.tags:
            if tag_entity.id is None or tag_entity.id not in existing_tag_ids_set:
                new_tags.append(self._company_tag_mapper.entity_to_row(tag_entity))

        company_row.tags = existing_tags + new_tags

        self._db.add(company_row)

        # Cache 무효화
        for tag in company.tags:
            for tag_name in tag.names:
                await self._redis.delete(f"{self._cache_namespace}:tag:{tag_name.name}")

    async def add_tag(
        self, name: str, tags: list[CompanyTagEntity]
    ) -> CompanyEntity | None:
        company = await self._get_by_name(name=name)
        if not company:
            return None

        existing_tag_ids = {tag.id for tag in company.tags}

        for tag in tags:
            if tag.id is None:
                tag_new_row = self._company_tag_mapper.entity_to_row(tag)
                self._db.add(tag_new_row)
                await self._db.flush()
                await self._db.refresh(tag_new_row)
                company.tags.append(tag_new_row)
                continue
            if tag.id in existing_tag_ids:
                continue

            stmt = (
                select(CompanyTag)
                .where(CompanyTag.id == tag.id)
                .options(selectinload(CompanyTag.names))
            )
            result = await self._db.execute(stmt)
            tag_row = result.scalar_one_or_none()
            if tag_row:
                company.tags.append(tag_row)

        await self._db.flush()
        company = await self._get_by_name(name=name)

        # Cache 무효화
        await self._redis.delete(f"{self._cache_namespace}:name:{name}")
        for tag in company.tags:
            for tag_name in tag.names:
                await self._redis.delete(f"{self._cache_namespace}:tag:{tag_name.name}")

        return self._company_mapper.row_to_entity(company)

    async def remove_tag(self, name: str, tag: str) -> CompanyEntity | None:
        company = await self._get_by_name(name=name)
        if not company:
            return None

        tag_row = next(
            (
                t
                for t in company.tags
                if any(tag_name.name == tag for tag_name in t.names)
            ),
            None,
        )
        if tag_row:
            company.tags.remove(tag_row)

        # Cache 무효화
        await self._redis.delete(f"{self._cache_namespace}:name:{name}")
        if tag_row:
            for tag_name in tag_row.names:
                await self._redis.delete(f"{self._cache_namespace}:tag:{tag_name.name}")

        return self._company_mapper.row_to_entity(company)
