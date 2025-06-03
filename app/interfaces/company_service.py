from typing import Protocol

from app.dto.company_dto import CompanySearchResultDto


class ICompanyService(Protocol):
    async def get_by_name(self, name: str, language_code: str) -> CompanySearchResultDto | None: ...

    async def get_by_partial_name(self, partial_name: str, language_code: str) -> list[CompanySearchResultDto]: ...

    async def get_by_tag(self, tag: str, language_code: str) -> list[CompanySearchResultDto]: ...