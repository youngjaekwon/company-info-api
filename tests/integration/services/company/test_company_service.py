class TestCompanyService:
    async def test_get_by_name_not_found(
        self, company_service, mock_company_repository
    ):
        # Given
        mock_company_repository.get_by_name.return_value = None

        # When
        result = await company_service.get_by_name("없는회사", "ko")

        # Then
        assert result is None
        mock_company_repository.get_by_name.assert_called_once_with(name="없는회사")

    async def test_get_by_name_found_with_matching_language(
        self, company_service, mock_company_repository, company_entity
    ):
        # Given
        mock_company_repository.get_by_name.return_value = company_entity

        # When
        result = await company_service.get_by_name("테스트회사", "ko")

        # Then
        assert result is not None
        assert result.company_name == "테스트회사"
        assert result.tags == ("태그1", "태그2")
        mock_company_repository.get_by_name.assert_called_once_with(name="테스트회사")

    async def test_get_by_name_found_with_non_matching_language_fallback(
        self, company_service, mock_company_repository, company_entity
    ):
        # Given
        mock_company_repository.get_by_name.return_value = company_entity

        # When
        result = await company_service.get_by_name("테스트회사", "fr")

        # Then
        assert result is not None
        assert result.company_name == "테스트회사"  # 첫 번째 이름 (ko)
        assert result.tags == ("태그1", "태그2")  # 첫 번째 태그 이름들 (ko)
        mock_company_repository.get_by_name.assert_called_once_with(name="테스트회사")

    async def test_get_by_name_found_with_english_language(
        self, company_service, mock_company_repository, company_entity
    ):
        # Given
        mock_company_repository.get_by_name.return_value = company_entity

        # When
        result = await company_service.get_by_name("테스트회사", "en")

        # Then
        assert result is not None
        assert result.company_name == "Test Company"
        assert result.tags == ("tag1", "tag2")
        mock_company_repository.get_by_name.assert_called_once_with(name="테스트회사")

    async def test_get_by_partial_name_empty_result(
        self, company_service, mock_company_repository
    ):
        # Given
        mock_company_repository.get_by_partial_name.return_value = []

        # When
        result = await company_service.get_by_partial_name("없는회사", "ko")

        # Then
        assert result == []
        mock_company_repository.get_by_partial_name.assert_called_once_with(
            partial_name="없는회사"
        )

    async def test_get_by_partial_name_found_with_matching_language(
        self, company_service, mock_company_repository, company_dtos
    ):
        # Given
        mock_company_repository.get_by_partial_name.return_value = company_dtos

        # When
        result = await company_service.get_by_partial_name("테스트", "ko")

        # Then
        assert len(result) == 3
        assert result[0].company_name == "테스트회사1"
        assert result[1].company_name == "테스트회사2"
        assert (
            result[2].company_name == "Test Company 3"
        )  # ko가 없어서 첫 번째 언어 (en)
        mock_company_repository.get_by_partial_name.assert_called_once_with(
            partial_name="테스트"
        )

    async def test_get_by_partial_name_found_with_fallback_language(
        self, company_service, mock_company_repository, company_dtos
    ):
        # Given
        mock_company_repository.get_by_partial_name.return_value = company_dtos

        # When
        result = await company_service.get_by_partial_name("테스트", "fr")

        # Then
        assert len(result) == 3
        assert result[0].company_name == "테스트회사1"  # 첫 번째 언어 (ko)
        assert result[1].company_name == "테스트회사2"  # 첫 번째 언어 (ko)
        assert result[2].company_name == "Test Company 3"  # 첫 번째 언어 (en)
        mock_company_repository.get_by_partial_name.assert_called_once_with(
            partial_name="테스트"
        )

    async def test_get_by_tag_empty_result(
        self, company_service, mock_company_repository
    ):
        # Given
        mock_company_repository.get_by_tag.return_value = []

        # When
        result = await company_service.get_by_tag("없는태그", "ko")

        # Then
        assert result == []
        mock_company_repository.get_by_tag.assert_called_once_with(tag="없는태그")

    async def test_get_by_tag_found_with_matching_language(
        self, company_service, mock_company_repository, company_dtos
    ):
        # Given
        mock_company_repository.get_by_tag.return_value = company_dtos

        # When
        result = await company_service.get_by_tag("태그1", "ko")

        # Then
        assert len(result) == 3
        assert result[0].company_name == "테스트회사1"
        assert result[1].company_name == "테스트회사2"
        assert (
            result[2].company_name == "Test Company 3"
        )  # ko가 없어서 첫 번째 언어 (en)
        mock_company_repository.get_by_tag.assert_called_once_with(tag="태그1")

    async def test_get_by_tag_found_with_japanese_tag_korean_response(
        self, company_service, mock_company_repository, company_dtos
    ):
        # Given
        mock_company_repository.get_by_tag.return_value = company_dtos

        # When
        result = await company_service.get_by_tag("タグ1", "ko")

        # Then
        assert len(result) == 3
        assert result[0].company_name == "테스트회사1"
        assert result[1].company_name == "테스트회사2"
        assert (
            result[2].company_name == "Test Company 3"
        )  # ko가 없어서 첫 번째 언어 (en)
        mock_company_repository.get_by_tag.assert_called_once_with(tag="タグ1")

    async def test_get_by_tag_found_with_fallback_language(
        self, company_service, mock_company_repository, company_dtos
    ):
        # Given
        mock_company_repository.get_by_tag.return_value = company_dtos

        # When
        result = await company_service.get_by_tag("tag1", "zh")

        # Then
        assert len(result) == 3
        assert result[0].company_name == "테스트회사1"  # 첫 번째 언어 (ko)
        assert result[1].company_name == "테스트회사2"  # 첫 번째 언어 (ko)
        assert result[2].company_name == "Test Company 3"  # 첫 번째 언어 (en)
        mock_company_repository.get_by_tag.assert_called_once_with(tag="tag1")

    async def test_get_by_name_with_invalid_company_names_returns_none(
        self, company_service, mock_company_repository
    ):
        # Given
        from app.domain.company_entity import CompanyEntity

        invalid_company = CompanyEntity(id="test-id", names=(), tags=())
        mock_company_repository.get_by_name.return_value = invalid_company

        # When
        result = await company_service.get_by_name("invalid", "ko")

        # Then
        assert result is None
        mock_company_repository.get_by_name.assert_called_once_with(name="invalid")

    async def test_get_by_partial_name_with_invalid_company_names_skips_invalid(
        self, company_service, mock_company_repository, company_dtos
    ):
        # Given
        from app.dto.company_dto import CompanyDto, CompanyNameDto

        valid_company = CompanyDto(
            names=(CompanyNameDto(language_code="ko", name="테스트회사1"),)
        )
        invalid_company = CompanyDto(names=())

        mock_company_repository.get_by_partial_name.return_value = [
            valid_company,
            invalid_company,
        ]

        # When
        result = await company_service.get_by_partial_name("테스트", "ko")

        # Then
        assert len(result) == 1
        assert result[0].company_name == "테스트회사1"
        mock_company_repository.get_by_partial_name.assert_called_once_with(
            partial_name="테스트"
        )

    async def test_get_by_tag_with_invalid_company_names_skips_invalid(
        self, company_service, mock_company_repository, company_dtos
    ):
        # Given
        from app.dto.company_dto import CompanyDto

        valid_company = company_dtos[0]
        invalid_company = CompanyDto(names=())

        mock_company_repository.get_by_tag.return_value = [
            valid_company,
            invalid_company,
        ]

        # When
        result = await company_service.get_by_tag("태그1", "ko")

        # Then
        assert len(result) == 1
        assert result[0].company_name == "테스트회사1"
        mock_company_repository.get_by_tag.assert_called_once_with(tag="태그1")

    async def test_create_with_existing_tag_adds_missing_language_codes(
        self, company_service, mock_company_repository, mock_company_tag_repository
    ):
        # Given
        from app.domain.company_entity import CompanyTagEntity, CompanyTagNameEntity
        from app.dto.company_dto import (
            CompanyDto,
            CompanyNameDto,
            CompanyTagDto,
            CompanyTagNameDto,
        )

        # 기존 태그 (ko만 있음)
        existing_tag = CompanyTagEntity(
            id=1, names=(CompanyTagNameEntity(language_code="ko", name="개발"),)
        )

        # 업데이트된 태그 (ko, en, ja 모두 있음)
        updated_tag = CompanyTagEntity(
            id=1,
            names=(
                CompanyTagNameEntity(language_code="ko", name="개발"),
                CompanyTagNameEntity(language_code="en", name="development"),
                CompanyTagNameEntity(language_code="ja", name="開発"),
            ),
        )

        mock_company_tag_repository.get_by_names.return_value = existing_tag
        mock_company_tag_repository.add_missing_names.return_value = updated_tag

        company_dto = CompanyDto(
            names=(CompanyNameDto(language_code="ko", name="테스트회사"),),
            tags=(
                CompanyTagDto(
                    names=(
                        CompanyTagNameDto(language_code="ko", name="개발"),
                        CompanyTagNameDto(language_code="en", name="development"),
                        CompanyTagNameDto(language_code="ja", name="開発"),
                    )
                ),
            ),
        )

        # When
        result = await company_service.create(company_dto, "ko")

        # Then
        assert result is not None
        mock_company_tag_repository.get_by_names.assert_called_once()
        mock_company_tag_repository.add_missing_names.assert_called_once()

        # add_missing_names 호출 인자 확인
        call_args = mock_company_tag_repository.add_missing_names.call_args
        assert call_args.kwargs["tag"] == existing_tag
        expected_names = [
            CompanyTagNameDto(language_code="ko", name="개발"),
            CompanyTagNameDto(language_code="en", name="development"),
            CompanyTagNameDto(language_code="ja", name="開発"),
        ]
        assert call_args.kwargs["names"] == expected_names

        mock_company_repository.save.assert_called_once()

    async def test_add_tags_with_existing_tag_adds_missing_language_codes(
        self, company_service, mock_company_repository, mock_company_tag_repository
    ):
        # Given
        from app.domain.company_entity import (
            CompanyEntity,
            CompanyNameEntity,
            CompanyTagEntity,
            CompanyTagNameEntity,
        )
        from app.dto.company_dto import CompanyTagDto, CompanyTagNameDto

        # 기존 태그 (ko, en만 있음)
        existing_tag = CompanyTagEntity(
            id=1,
            names=(
                CompanyTagNameEntity(language_code="ko", name="스타트업"),
                CompanyTagNameEntity(language_code="en", name="startup"),
            ),
        )

        # 업데이트된 태그 (ko, en, fr, de 모두 있음)
        updated_tag = CompanyTagEntity(
            id=1,
            names=(
                CompanyTagNameEntity(language_code="ko", name="스타트업"),
                CompanyTagNameEntity(language_code="en", name="startup"),
                CompanyTagNameEntity(language_code="fr", name="startup"),
                CompanyTagNameEntity(language_code="de", name="startup"),
            ),
        )

        # 업데이트된 회사 엔티티
        updated_company = CompanyEntity(
            id="test-id",
            names=(CompanyNameEntity(language_code="ko", name="테스트회사"),),
            tags=(updated_tag,),
        )

        mock_company_tag_repository.get_by_names.return_value = existing_tag
        mock_company_tag_repository.add_missing_names.return_value = updated_tag
        mock_company_repository.add_tag.return_value = updated_company

        tags = [
            CompanyTagDto(
                names=(
                    CompanyTagNameDto(language_code="ko", name="스타트업"),
                    CompanyTagNameDto(language_code="en", name="startup"),
                    CompanyTagNameDto(language_code="fr", name="startup"),
                    CompanyTagNameDto(language_code="de", name="startup"),
                )
            )
        ]

        # When
        result = await company_service.add_tags("테스트회사", tags, "ko")

        # Then
        assert result is not None
        mock_company_tag_repository.get_by_names.assert_called_once()
        mock_company_tag_repository.add_missing_names.assert_called_once()

        # add_missing_names 호출 인자 확인
        call_args = mock_company_tag_repository.add_missing_names.call_args
        assert call_args.kwargs["tag"] == existing_tag
        expected_names = [
            CompanyTagNameDto(language_code="ko", name="스타트업"),
            CompanyTagNameDto(language_code="en", name="startup"),
            CompanyTagNameDto(language_code="fr", name="startup"),
            CompanyTagNameDto(language_code="de", name="startup"),
        ]
        assert call_args.kwargs["names"] == expected_names

        mock_company_repository.add_tag.assert_called_once_with(
            name="테스트회사", tags=[updated_tag]
        )

    async def test_create_with_new_tag_does_not_call_add_missing_names(
        self, company_service, mock_company_repository, mock_company_tag_repository
    ):
        # Given
        from app.dto.company_dto import (
            CompanyDto,
            CompanyNameDto,
            CompanyTagDto,
            CompanyTagNameDto,
        )

        mock_company_tag_repository.get_by_names.return_value = None

        company_dto = CompanyDto(
            names=(CompanyNameDto(language_code="ko", name="테스트회사"),),
            tags=(
                CompanyTagDto(
                    names=(
                        CompanyTagNameDto(language_code="ko", name="새태그"),
                        CompanyTagNameDto(language_code="en", name="new tag"),
                    )
                ),
            ),
        )

        # When
        result = await company_service.create(company_dto, "ko")

        # Then
        assert result is not None
        mock_company_tag_repository.get_by_names.assert_called_once()
        mock_company_tag_repository.add_missing_names.assert_not_called()
        mock_company_repository.save.assert_called_once()
