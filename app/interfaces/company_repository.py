from typing import Protocol

from app.domain.company_entity import CompanyEntity, CompanyTagEntity
from app.dto.company_dto import CompanyDto


class ICompanyRepository(Protocol):
    async def get_by_name(self, name: str) -> CompanyEntity | None: ...

    async def get_by_partial_name(self, partial_name: str) -> list[CompanyDto]: ...

    async def get_by_tag(self, tag: str) -> list[CompanyDto]: ...

    async def save(self, company: CompanyEntity) -> None: ...

    async def add_tag(
        self, name: str, tags: list[CompanyTagEntity]
    ) -> CompanyEntity | None: ...

    async def remove_tag(self, name: str, tag: str) -> CompanyEntity | None: ...
