from app.core.schema import SchemaBase


class SearchedCompanyResponse(SchemaBase):
    company_name: str

class CompanyResponse(SchemaBase):
    company_name: str
    tags: list[str] = []
