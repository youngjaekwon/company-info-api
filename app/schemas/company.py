from pydantic import field_validator

from app.core.schema import NamesDict, SchemaBase


class SearchedCompanyResponse(SchemaBase):
    company_name: str


class CompanyResponse(SchemaBase):
    company_name: str
    tags: list[str] = []


class CompanyTagRequest(SchemaBase):
    tag_name: NamesDict

    @field_validator("tag_name", mode="after")
    @classmethod
    def _no_empty_tag_name(cls, value: NamesDict) -> NamesDict:
        if not value.root:
            raise ValueError("Tag name cannot be empty")
        return value


class CreateCompanyRequest(SchemaBase):
    company_name: NamesDict
    tags: list[CompanyTagRequest] = []

    @field_validator("company_name", mode="after")
    @classmethod
    def _no_empty_company_name(cls, value: NamesDict) -> NamesDict:
        if not value.root:
            raise ValueError("Company name cannot be empty")
        return value
