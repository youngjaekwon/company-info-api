from pydantic import ConfigDict, BaseModel


class SchemaBase(BaseModel):
    model_config = ConfigDict(
        from_attributes=True, extra="forbid", populate_by_name=True
    )
