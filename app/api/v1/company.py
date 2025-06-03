from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import WantedLanguage
from app.containers import AppContainer
from app.interfaces.company_service import ICompanyService
from app.schemas.company import CompanyResponse, SearchedCompanyResponse

router = APIRouter(tags=["Company"])


@router.get("/search", response_model=list[SearchedCompanyResponse])
@inject
async def search_companies(
    query: Annotated[str, Query()],
    language_code: WantedLanguage,
    company_service: Annotated[
        ICompanyService, Depends(Provide[AppContainer.services.company_service])
    ],
):
    return await company_service.get_by_partial_name(
        partial_name=query, language_code=language_code
    )


@router.get("/companies/{company_name}", response_model=CompanyResponse)
@inject
async def get_company(
    company_name: str,
    language_code: WantedLanguage,
    company_service: Annotated[
        ICompanyService, Depends(Provide[AppContainer.services.company_service])
    ],
):
    company = await company_service.get_by_name(
        name=company_name, language_code=language_code
    )
    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return company


@router.get("/tags", response_model=list[SearchedCompanyResponse])
@inject
async def get_companies_by_tag(
    query: Annotated[str, Query()],
    language_code: WantedLanguage,
    company_service: Annotated[
        ICompanyService, Depends(Provide[AppContainer.services.company_service])
    ],
):
    return await company_service.get_by_tag(tag=query, language_code=language_code)
