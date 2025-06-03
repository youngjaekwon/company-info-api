from unittest.mock import AsyncMock

import pytest


@pytest.fixture()
def company_mapper():
    from app.mappers.company_mapper import CompanyMapper

    return CompanyMapper()


@pytest.fixture()
def company_tag_mapper():
    from app.mappers.company_tag_mapper import CompanyTagMapper

    return CompanyTagMapper()


@pytest.fixture()
def mock_company_repository():
    from app.interfaces.company_repository import ICompanyRepository

    return AsyncMock(spec=ICompanyRepository)


@pytest.fixture()
def mock_company_tag_repository():
    from app.interfaces.company_tag_repository import ICompanyTagRepository

    return AsyncMock(spec=ICompanyTagRepository)


@pytest.fixture()
def company_service(
    async_session,
    mock_company_repository,
    mock_company_tag_repository,
    company_mapper,
    company_tag_mapper,
):
    from app.services.company_service import CompanyService

    return CompanyService(
        db=async_session,
        company_repo=mock_company_repository,
        company_tag_repo=mock_company_tag_repository,
        company_mapper=company_mapper,
        company_tag_mapper=company_tag_mapper,
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
