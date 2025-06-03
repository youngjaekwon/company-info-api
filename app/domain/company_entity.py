from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class CompanyNameEntity:
    language_code: str
    name: str
    id: int | None = None

    def __post_init__(self):
        if not self.name:
            raise ValueError("Company name cannot be empty")
        if not self.language_code:
            raise ValueError("Language code cannot be empty")


@dataclass(frozen=True, slots=True)
class CompanyTagNameEntity:
    language_code: str
    name: str
    id: int | None = None

    def __post_init__(self):
        if not self.name:
            raise ValueError("Company tag name cannot be empty")
        if not self.language_code:
            raise ValueError("Language code cannot be empty")


@dataclass(frozen=True, slots=True)
class CompanyTagEntity:
    names: tuple[CompanyTagNameEntity, ...] = field(default_factory=tuple)
    id: int | None = None


@dataclass(frozen=True)
class CompanyEntity:
    names: tuple[CompanyNameEntity, ...] = field(default_factory=tuple)
    tags: tuple[CompanyTagEntity, ...] = field(default_factory=tuple)
    id: str | None = None
