from typing import Annotated

from fastapi.params import Header

WantedLanguage = Annotated[str, Header(..., alias="x-wanted-language")]
