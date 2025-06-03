import json
import uuid

from app.db.models import Company, CompanyName, CompanyTag, CompanyTagName
from app.domain.company_entity import (
    CompanyEntity,
    CompanyNameEntity,
    CompanyTagEntity,
    CompanyTagNameEntity,
)
from app.dto.company_dto import CompanyDto, CompanyNameDto, CompanySearchResultDto


class CompanyMapper:
    def _get_matched_name(
        self, obj: CompanyDto | CompanyEntity | CompanyTagEntity, language_code: str
    ) -> str:
        if not obj.names:
            raise ValueError("Company/Tag must have at least one name")

        matched_name = next(
            (name for name in obj.names if name.language_code == language_code),
            None,
        )
        if matched_name is None:
            return obj.names[0].name
        return matched_name.name

    def entity_to_search_result(
        self, entity: CompanyEntity, language_code: str
    ) -> CompanySearchResultDto:
        name = self._get_matched_name(obj=entity, language_code=language_code)
        tags = []
        for tag in entity.tags:
            matched_tag_name = self._get_matched_name(
                obj=tag, language_code=language_code
            )
            tags.append(matched_tag_name)

        return CompanySearchResultDto(
            company_name=name,
            tags=tuple(tags),
        )

    def dto_to_search_result(
        self, dto: CompanyDto, language_code: str
    ) -> CompanySearchResultDto:
        return CompanySearchResultDto(
            company_name=self._get_matched_name(obj=dto, language_code=language_code)
        )

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
                        company_tag_id=tag_name.company_tag_id,
                    )
                    for tag_name in tag.names
                ),
                id=tag.id,
            )
            for tag in row.tags
        )
        return CompanyEntity(names=names, tags=tags, id=str(row.id))

    def entity_to_row(self, entity: CompanyEntity) -> Company:
        # 문자열 ID를 UUID 객체로 변환
        company_id = None
        if entity.id:
            if isinstance(entity.id, str):
                company_id = uuid.UUID(entity.id)
            else:
                company_id = entity.id

        company = Company(id=company_id)
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
                        company_tag_id=tag_name.company_tag_id,
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

    def entity_to_json(self, entity: CompanyEntity) -> str:
        data = {
            "id": entity.id,
            "names": [
                {"language_code": name.language_code, "name": name.name}
                for name in entity.names
            ],
            "tags": [
                {
                    "id": tag.id,
                    "names": [
                        {"language_code": tag_name.language_code, "name": tag_name.name}
                        for tag_name in tag.names
                    ],
                }
                for tag in entity.tags
            ],
        }
        return json.dumps(data)

    def dtos_to_json(self, dtos: list[CompanyDto]) -> str:
        data = [
            {
                "names": [
                    {"language_code": name.language_code, "name": name.name}
                    for name in dto.names
                ]
            }
            for dto in dtos
        ]
        return json.dumps(data)

    def json_to_entity(self, data: str) -> CompanyEntity:
        data = json.loads(data)
        names = tuple(
            CompanyNameEntity(language_code=name["language_code"], name=name["name"])
            for name in data["names"]
        )
        tags = tuple(
            CompanyTagEntity(
                id=tag["id"],
                names=tuple(
                    CompanyTagNameEntity(
                        language_code=tag_name["language_code"],
                        name=tag_name["name"],
                    )
                    for tag_name in tag["names"]
                ),
            )
            for tag in data.get("tags", [])
        )
        return CompanyEntity(names=names, tags=tags, id=data.get("id"))

    def json_to_dtos(self, data: str) -> list[CompanyDto]:
        data = json.loads(data)
        return [
            CompanyDto(
                names=tuple(
                    CompanyNameDto(
                        language_code=name["language_code"], name=name["name"]
                    )
                    for name in item["names"]
                )
            )
            for item in data
        ]

    def dto_to_entity(
        self, dto: CompanyDto, tags: list[CompanyTagEntity] | None = None
    ) -> CompanyEntity:
        names = tuple(
            CompanyNameEntity(language_code=name.language_code, name=name.name)
            for name in dto.names
        )
        return CompanyEntity(names=names, tags=tags or tuple())
