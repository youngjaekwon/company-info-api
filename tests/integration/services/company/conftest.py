from unittest.mock import AsyncMock

import pytest

from app.mappers.company_mapper import CompanyMapper
from app.services.company_service import CompanyService


@pytest.fixture()
def company_mapper():
    return CompanyMapper()


@pytest.fixture()
def mock_company_repository():
    return AsyncMock()


@pytest.fixture()
def company_service(mock_company_repository, company_mapper):
    return CompanyService(
        company_repo=mock_company_repository, company_mapper=company_mapper
    )


@pytest.fixture()
def company_entity():
    from app.domain.company_entity import (
        CompanyEntity,
        CompanyNameEntity,
        CompanyTagEntity,
        CompanyTagNameEntity,
    )

    return CompanyEntity(
        id="test-id",
        names=(
            CompanyNameEntity(id=1, language_code="ko", name="테스트회사"),
            CompanyNameEntity(id=2, language_code="en", name="Test Company"),
            CompanyNameEntity(id=3, language_code="jp", name="テスト会社"),
        ),
        tags=(
            CompanyTagEntity(
                id=1,
                names=(
                    CompanyTagNameEntity(id=1, language_code="ko", name="태그1"),
                    CompanyTagNameEntity(id=2, language_code="en", name="tag1"),
                    CompanyTagNameEntity(id=3, language_code="jp", name="タグ1"),
                ),
            ),
            CompanyTagEntity(
                id=2,
                names=(
                    CompanyTagNameEntity(id=4, language_code="ko", name="태그2"),
                    CompanyTagNameEntity(id=5, language_code="en", name="tag2"),
                ),
            ),
        ),
    )


@pytest.fixture()
def company_dtos():
    from app.dto.company_dto import CompanyDto, CompanyNameDto

    return [
        CompanyDto(
            names=(
                CompanyNameDto(language_code="ko", name="테스트회사1"),
                CompanyNameDto(language_code="en", name="Test Company 1"),
            )
        ),
        CompanyDto(
            names=(
                CompanyNameDto(language_code="ko", name="테스트회사2"),
                CompanyNameDto(language_code="jp", name="テスト会社2"),
            )
        ),
        CompanyDto(names=(CompanyNameDto(language_code="en", name="Test Company 3"),)),
    ]
