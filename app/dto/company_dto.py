from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CompanyNameDto:
    language_code: str
    name: str


@dataclass(frozen=True, slots=True)
class CompanyDto:
    names: tuple[CompanyNameDto, ...]
