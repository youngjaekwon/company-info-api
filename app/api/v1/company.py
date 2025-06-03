from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import WantedLanguage, get_company_service
from app.dto.company_dto import (
    CompanyDto,
    CompanyNameDto,
    CompanyTagDto,
    CompanyTagNameDto,
)
from app.interfaces.company_service import ICompanyService
from app.schemas.company import (
    CompanyResponse,
    CompanyTagRequest,
    CreateCompanyRequest,
    SearchedCompanyResponse,
)

router = APIRouter(tags=["Company"])


@router.get("/search", response_model=list[SearchedCompanyResponse])
async def search_companies(
    query: Annotated[str, Query()],
    language_code: WantedLanguage,
    company_service: Annotated[ICompanyService, Depends(get_company_service)],
):
    return await company_service.get_by_partial_name(
        partial_name=query, language_code=language_code
    )


@router.post("/companies", response_model=CompanyResponse)
async def create_company(
    body: CreateCompanyRequest,
    language_code: WantedLanguage,
    company_service: Annotated[ICompanyService, Depends(get_company_service)],
):
    names = tuple(
        CompanyNameDto(language_code=language_code, name=name)
        for language_code, name in body.company_name.root.items()
    )
    tags = tuple(
        CompanyTagDto(
            names=tuple(
                CompanyTagNameDto(language_code=language_code, name=name)
                for language_code, name in tag.tag_name.root.items()
            )
        )
        for tag in body.tags
    )
    company = CompanyDto(names=names, tags=tags)
    created_company = await company_service.create(
        company=company, language_code=language_code
    )
    return created_company


@router.get("/companies/{company_name}", response_model=CompanyResponse)
async def get_company(
    company_name: str,
    language_code: WantedLanguage,
    company_service: Annotated[ICompanyService, Depends(get_company_service)],
):
    company = await company_service.get_by_name(
        name=company_name, language_code=language_code
    )
    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return company


@router.put("/companies/{company_name}/tags", response_model=CompanyResponse)
async def add_tags_to_company(
    company_name: str,
    body: list[CompanyTagRequest],
    language_code: WantedLanguage,
    company_service: Annotated[ICompanyService, Depends(get_company_service)],
):
    tags = [
        CompanyTagDto(
            names=tuple(
                CompanyTagNameDto(language_code=language_code, name=name)
                for language_code, name in tag.tag_name.root.items()
            )
        )
        for tag in body
    ]
    updated_company = await company_service.add_tags(
        name=company_name, tags=tags, language_code=language_code
    )
    if updated_company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return updated_company


@router.delete(
    "/companies/{company_name}/tags/{tag_name}", response_model=CompanyResponse
)
async def remove_tag_from_company(
    company_name: str,
    tag_name: str,
    language_code: WantedLanguage,
    company_service: Annotated[ICompanyService, Depends(get_company_service)],
):
    updated_company = await company_service.remove_tag(
        name=company_name, tag=tag_name, language_code=language_code
    )
    if updated_company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return updated_company


@router.get("/tags", response_model=list[SearchedCompanyResponse])
async def get_companies_by_tag(
    query: Annotated[str, Query()],
    language_code: WantedLanguage,
    company_service: Annotated[ICompanyService, Depends(get_company_service)],
):
    return await company_service.get_by_tag(tag=query, language_code=language_code)
