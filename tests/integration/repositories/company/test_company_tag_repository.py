from sqlalchemy import select


class TestCompanyTagRepository:
    async def test_get_by_names_not_found_with_empty_names(
        self, company_tag_repository
    ):
        # Given
        names = []

        # When
        result = await company_tag_repository.get_by_names(names)

        # Then
        assert result is None

    async def test_get_by_names_not_found_with_nonexistent_name(
        self, company_tag_repository
    ):
        # Given
        from app.dto.company_dto import CompanyTagNameDto

        names = [CompanyTagNameDto(language_code="ko", name="존재하지않는태그")]

        # When
        result = await company_tag_repository.get_by_names(names)

        # Then
        assert result is None

    async def test_get_by_names_found_with_single_name(
        self, company_tag_repository, company_tags
    ):
        # Given
        from app.dto.company_dto import CompanyTagNameDto

        tag = company_tags[0]
        tag_name = tag.names[0]
        names = [
            CompanyTagNameDto(language_code=tag_name.language_code, name=tag_name.name)
        ]

        # When
        result = await company_tag_repository.get_by_names(names)

        # Then
        assert result is not None
        assert result.id == tag.id
        assert len(result.names) == 1
        assert result.names[0].name == tag_name.name
        assert result.names[0].language_code == tag_name.language_code

    async def test_get_by_names_found_with_multiple_names_exact_match(
        self, company_tag_repository, multi_language_company_tag
    ):
        # Given
        from app.dto.company_dto import CompanyTagNameDto

        tag = multi_language_company_tag
        names = [
            CompanyTagNameDto(language_code=name.language_code, name=name.name)
            for name in tag.names
        ]

        # When
        result = await company_tag_repository.get_by_names(names)

        # Then
        assert result is not None
        assert result.id == tag.id
        assert len(result.names) == len(tag.names)
        result_names = {(name.language_code, name.name) for name in result.names}
        expected_names = {(name.language_code, name.name) for name in tag.names}
        assert result_names == expected_names

    async def test_get_by_names_not_found_with_partial_match(
        self, company_tag_repository, multi_language_company_tag
    ):
        # Given
        from app.dto.company_dto import CompanyTagNameDto

        tag = multi_language_company_tag
        # 다국어 태그 중 일부만 사용 (부분 매치)
        names = [
            CompanyTagNameDto(
                language_code=tag.names[0].language_code, name=tag.names[0].name
            )
        ]

        # When
        result = await company_tag_repository.get_by_names(names)

        # Then
        # 부분 매치는 조회되지 않아야 함 (모든 이름이 일치해야 함)
        assert result is None

    async def test_get_by_names_not_found_with_extra_name(
        self, company_tag_repository, multi_language_company_tag
    ):
        # Given
        from app.dto.company_dto import CompanyTagNameDto

        tag = multi_language_company_tag
        names = [
            CompanyTagNameDto(language_code=name.language_code, name=name.name)
            for name in tag.names
        ]
        # 존재하지 않는 추가 이름 추가
        names.append(CompanyTagNameDto(language_code="fr", name="tag français"))

        # When
        result = await company_tag_repository.get_by_names(names)

        # Then
        # 추가 이름이 있으면 조회되지 않아야 함
        assert result is None

    async def test_get_by_names_not_found_with_wrong_language_code(
        self, company_tag_repository, company_tags
    ):
        # Given
        from app.dto.company_dto import CompanyTagNameDto

        tag = company_tags[0]
        tag_name = tag.names[0]
        names = [
            CompanyTagNameDto(
                language_code="en",  # 잘못된 언어 코드
                name=tag_name.name,
            )
        ]

        # When
        result = await company_tag_repository.get_by_names(names)

        # Then
        assert result is None

    async def test_get_by_names_not_found_with_mixed_names_from_different_tags(
        self, company_tag_repository, company_tags, multi_language_company_tag
    ):
        # Given
        from app.dto.company_dto import CompanyTagNameDto

        # 서로 다른 태그의 이름들을 조합
        names = [
            CompanyTagNameDto(
                language_code=company_tags[0].names[0].language_code,
                name=company_tags[0].names[0].name,
            ),
            CompanyTagNameDto(
                language_code=multi_language_company_tag.names[0].language_code,
                name=multi_language_company_tag.names[0].name,
            ),
        ]

        # When
        result = await company_tag_repository.get_by_names(names)

        # Then
        # 다른 태그의 이름들을 조합하면 조회되지 않아야 함
        assert result is None

    async def test_save_all_with_single_tag(
        self, company_tag_repository, async_session
    ):
        # Given
        from app.db.models import CompanyTag, CompanyTagName
        from app.domain.company_entity import CompanyTagEntity, CompanyTagNameEntity

        tag_entity = CompanyTagEntity(
            names=(CompanyTagNameEntity(language_code="ko", name="새태그"),)
        )

        # When
        await company_tag_repository.save_all([tag_entity])
        await async_session.flush()

        # Then
        stmt = (
            select(CompanyTag)
            .join(CompanyTag.names)
            .where(CompanyTagName.name == "새태그")
        )
        result = await async_session.execute(stmt)
        saved_tag = result.scalars().first()
        assert saved_tag is not None
        assert len(saved_tag.names) == 1
        assert saved_tag.names[0].name == "새태그"
        assert saved_tag.names[0].language_code == "ko"

    async def test_save_all_with_multiple_tags(
        self, company_tag_repository, async_session
    ):
        # Given
        from app.db.models import CompanyTag, CompanyTagName
        from app.domain.company_entity import CompanyTagEntity, CompanyTagNameEntity

        tag_entities = [
            CompanyTagEntity(
                names=(CompanyTagNameEntity(language_code="ko", name="새태그1"),)
            ),
            CompanyTagEntity(
                names=(
                    CompanyTagNameEntity(language_code="ko", name="새태그2"),
                    CompanyTagNameEntity(language_code="en", name="new tag 2"),
                )
            ),
        ]

        # When
        await company_tag_repository.save_all(tag_entities)
        await async_session.flush()

        # Then
        stmt = (
            select(CompanyTag)
            .join(CompanyTag.names)
            .where(CompanyTagName.name.in_(["새태그1", "새태그2"]))
        )
        result = await async_session.execute(stmt)
        saved_tags = result.scalars().all()
        assert len(saved_tags) == 2

        # 첫 번째 태그 확인
        tag1 = next(
            tag
            for tag in saved_tags
            if any(name.name == "새태그1" for name in tag.names)
        )
        assert len(tag1.names) == 1
        assert tag1.names[0].name == "새태그1"
        assert tag1.names[0].language_code == "ko"

        # 두 번째 태그 확인
        tag2 = next(
            tag
            for tag in saved_tags
            if any(name.name == "새태그2" for name in tag.names)
        )
        assert len(tag2.names) == 2
        tag2_names = {name.name: name.language_code for name in tag2.names}
        assert "새태그2" in tag2_names
        assert "new tag 2" in tag2_names
        assert tag2_names["새태그2"] == "ko"
        assert tag2_names["new tag 2"] == "en"
