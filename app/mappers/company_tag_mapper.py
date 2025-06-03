from app.db.models import CompanyTag, CompanyTagName
from app.domain.company_entity import CompanyTagEntity, CompanyTagNameEntity


class CompanyTagMapper:
    def row_to_entity(self, row: CompanyTag) -> CompanyTagEntity:
        names = tuple(
            CompanyTagNameEntity(
                language_code=name.language_code,
                name=name.name,
                id=name.id,
                company_tag_id=name.company_tag_id,
            )
            for name in row.names
        )
        return CompanyTagEntity(names=names, id=row.id)

    def entity_to_row(self, entity: CompanyTagEntity) -> CompanyTag:
        tag = CompanyTag(id=entity.id)
        tag.names = [
            CompanyTagName(
                language_code=name.language_code,
                name=name.name,
                id=name.id,
                company_tag_id=name.company_tag_id,
            )
            for name in entity.names
        ]
        return tag
