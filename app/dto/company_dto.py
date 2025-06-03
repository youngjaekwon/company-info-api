from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class CompanyNameDto:
    language_code: str
    name: str


@dataclass(frozen=True, slots=True)
class CompanyDto:
    names: tuple[CompanyNameDto, ...]


@dataclass(frozen=True, slots=True)
class CompanySearchResultDto:
    company_name: str
    tags: tuple[str, ...] = field(default_factory=tuple)
