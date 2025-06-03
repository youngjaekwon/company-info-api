from __future__ import annotations

import uuid

from sqlalchemy import (
    UUID,
    Column,
    ForeignKey,
    Integer,
    String,
    Table,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

company_tag = Table(
    "company_tag",
    Base.metadata,
    Column("company_id", ForeignKey("companies.id"), primary_key=True),
    Column("company_tag_id", ForeignKey("company_tags.id"), primary_key=True),
)


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), default=uuid.uuid4, primary_key=True
    )

    names: Mapped[list[CompanyName]] = relationship(
        "CompanyName",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    tags: Mapped[list[CompanyTag]] = relationship(
        "CompanyTag",
        secondary=company_tag,
        back_populates="companies",
    )


class CompanyName(Base):
    __tablename__ = "company_names"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    language_code: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    name: Mapped[str] = mapped_column(nullable=False)

    __table_args__ = (
        UniqueConstraint("company_id", "language_code"),
        UniqueConstraint("name", "language_code"),
        Index("ix_company_names_name_exact", "name"),  # btree (정확 일치)
        Index(
            "ix_company_names_name_trgm",
            "name",
            postgresql_using="gin",
            postgresql_ops={"name": "gin_trgm_ops"},
        ),  # trigram (ilike 대응용)
    )


class CompanyTag(Base):
    __tablename__ = "company_tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    names: Mapped[list[CompanyTagName]] = relationship(
        "CompanyTagName",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    companies: Mapped[list[Company]] = relationship(
        "Company",
        secondary=company_tag,
        back_populates="tags",
    )


class CompanyTagName(Base):
    __tablename__ = "company_tag_names"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_tag_id: Mapped[int] = mapped_column(
        ForeignKey("company_tags.id"), nullable=False
    )
    language_code: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    name: Mapped[str] = mapped_column(nullable=False)

    __table_args__ = (
        UniqueConstraint("company_tag_id", "language_code"),
        UniqueConstraint("name", "language_code"),
        Index("ix_company_tag_names_name_exact", "name"),
    )
