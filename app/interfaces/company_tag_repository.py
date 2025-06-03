from typing import Protocol

from app.domain.company_entity import CompanyTagEntity
from app.dto.company_dto import CompanyTagNameDto


class ICompanyTagRepository(Protocol):
    async def get_by_names(
        self, names: list[CompanyTagNameDto]
    ) -> CompanyTagEntity | None: ...

    async def save(self, tag: CompanyTagEntity) -> CompanyTagEntity: ...

    async def save_all(self, tags: list[CompanyTagEntity]) -> None: ...

    async def add_missing_names(
        self, tag: CompanyTagEntity, names: list[CompanyTagNameDto]
    ) -> CompanyTagEntity: ...
