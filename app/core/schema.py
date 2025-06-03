from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, RootModel, field_validator


class SchemaBase(BaseModel):
    model_config = ConfigDict(
        from_attributes=True, extra="forbid", populate_by_name=True
    )


LangCode = Annotated[str, Field(pattern=r"^[a-z]{2,3}$")]


class NamesDict(RootModel[dict[LangCode, str]]):
    @field_validator("root", mode="after")
    @classmethod
    def _no_empty_values(cls, value: dict[str, str]) -> dict[str, str]:
        for lang, name in value.items():
            if not name.strip():
                raise ValueError(f"Name for language '{lang}' cannot be empty")
        return value
