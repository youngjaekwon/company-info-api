from app.db.models import Company, CompanyName, CompanyTag, CompanyTagName
from app.domain.company_entity import (
    CompanyEntity,
    CompanyTagEntity,
    CompanyTagNameEntity,
    CompanyNameEntity,
)
from app.dto.company_dto import CompanyDto, CompanyNameDto


class CompanyMapper:
    def row_to_entity(self, row: Company) -> CompanyEntity:
        names = tuple(
            CompanyNameEntity(
                language_code=name.language_code, name=name.name, id=name.id
            )
            for name in row.names
        )
        tags = tuple(
            CompanyTagEntity(
                names=tuple(
                    CompanyTagNameEntity(
                        language_code=tag_name.language_code,
                        name=tag_name.name,
                        id=tag_name.id,
                    )
                    for tag_name in tag.names
                ),
                id=tag.id,
            )
            for tag in row.tags
        )
        return CompanyEntity(names=names, tags=tags, id=row.id)

    def entity_to_row(self, entity: CompanyEntity) -> Company:
        company = Company(id=entity.id)
        company.names = [
            CompanyName(language_code=name.language_code, name=name.name, id=name.id)
            for name in entity.names
        ]
        company.tags = [
            CompanyTag(
                names=[
                    CompanyTagName(
                        language_code=tag_name.language_code,
                        name=tag_name.name,
                        id=tag_name.id,
                    )
                    for tag_name in tag.names
                ],
                id=tag.id,
            )
            for tag in entity.tags
        ]
        return company

    def row_to_search_result_dto(self, row: Company) -> CompanyDto:
        return CompanyDto(
            names=tuple(
                CompanyNameDto(
                    language_code=name.language_code,
                    name=name.name,
                )
                for name in row.names
            )
        )
