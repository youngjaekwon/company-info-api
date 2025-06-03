from typing import Annotated

import redis.asyncio as redis
from fastapi import Depends
from fastapi.params import Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.db.redis import get_redis_client
from app.db.session import get_db
from app.mappers.company_mapper import CompanyMapper
from app.mappers.company_tag_mapper import CompanyTagMapper
from app.repositories.company_repository import CompanyRepository
from app.repositories.company_tag_repository import CompanyTagRepository
from app.services.company_service import CompanyService

WantedLanguage = Annotated[str, Header(..., alias="x-wanted-language")]


# Mappers
def get_company_mapper() -> CompanyMapper:
    return CompanyMapper()


def get_company_tag_mapper() -> CompanyTagMapper:
    return CompanyTagMapper()


# Repositories
def get_company_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
    redis_client: Annotated[redis.Redis, Depends(get_redis_client)],
    company_mapper: Annotated[CompanyMapper, Depends(get_company_mapper)],
    company_tag_mapper: Annotated[CompanyTagMapper, Depends(get_company_tag_mapper)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> CompanyRepository:
    return CompanyRepository(
        db=db,
        redis_client=redis_client,
        company_mapper=company_mapper,
        company_tag_mapper=company_tag_mapper,
        settings=settings,
    )


def get_company_tag_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
    company_tag_mapper: Annotated[CompanyTagMapper, Depends(get_company_tag_mapper)],
) -> CompanyTagRepository:
    return CompanyTagRepository(
        db=db,
        company_tag_mapper=company_tag_mapper,
    )


# Services
def get_company_service(
    db: Annotated[AsyncSession, Depends(get_db)],
    company_repo: Annotated[CompanyRepository, Depends(get_company_repository)],
    company_tag_repo: Annotated[
        CompanyTagRepository, Depends(get_company_tag_repository)
    ],
    company_mapper: Annotated[CompanyMapper, Depends(get_company_mapper)],
    company_tag_mapper: Annotated[CompanyTagMapper, Depends(get_company_tag_mapper)],
) -> CompanyService:
    return CompanyService(
        db=db,
        company_repo=company_repo,
        company_tag_repo=company_tag_repo,
        company_mapper=company_mapper,
        company_tag_mapper=company_tag_mapper,
    )
