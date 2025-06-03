from typing import Protocol

from app.dto.company_dto import CompanySearchResultDto, CompanyDto, CompanyTagDto


class ICompanyService(Protocol):
    async def get_by_name(
        self, name: str, language_code: str
    ) -> CompanySearchResultDto | None: ...

    async def get_by_partial_name(
        self, partial_name: str, language_code: str
    ) -> list[CompanySearchResultDto]: ...

    async def get_by_tag(
        self, tag: str, language_code: str
    ) -> list[CompanySearchResultDto]: ...

    async def create(
        self, company: CompanyDto, language_code: str
    ) -> CompanySearchResultDto: ...

    async def add_tags(
        self, name: str, tags: list[CompanyTagDto], language_code: str
    ) -> CompanySearchResultDto | None: ...

    async def remove_tag(
        self, name: str, tag: str, language_code: str
    ) -> CompanySearchResultDto | None: ...
