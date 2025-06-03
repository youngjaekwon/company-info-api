from app.db.models import CompanyTag, CompanyTagName
from app.domain.company_entity import CompanyTagEntity, CompanyTagNameEntity
from app.dto.company_dto import CompanyTagDto


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
        if entity.id is not None:
            tag = CompanyTag(id=entity.id)
        else:
            tag = CompanyTag()

        tag.names = [
            CompanyTagName(
                language_code=name.language_code,
                name=name.name,
                company_tag_id=name.company_tag_id,
                **({"id": name.id} if name.id is not None else {}),
            )
            for name in entity.names
        ]
        return tag

    def dto_to_entity(self, dto: CompanyTagDto) -> CompanyTagEntity:
        names = tuple(
            CompanyTagNameEntity(
                language_code=name.language_code,
                name=name.name,
            )
            for name in dto.names
        )
        return CompanyTagEntity(names=names)
