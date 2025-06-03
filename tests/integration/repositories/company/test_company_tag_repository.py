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

    async def test_get_by_names_found_with_partial_match(
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
        # 부분 매치도 가장 일치하는 태그를 반환해야 함
        assert result is not None
        assert result.id == tag.id
        # 전체 이름들이 로드되어야 함
        assert len(result.names) == len(tag.names)

    async def test_get_by_names_found_with_best_match_when_extra_name(
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
        # 가장 많이 매칭되는 태그를 반환해야 함 (존재하지 않는 이름은 무시)
        assert result is not None
        assert result.id == tag.id
        assert len(result.names) == len(tag.names)
        result_names = {(name.language_code, name.name) for name in result.names}
        expected_names = {(name.language_code, name.name) for name in tag.names}
        assert result_names == expected_names

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

    async def test_get_by_names_found_with_best_match_from_mixed_names(
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
        # 가장 많이 매칭되는 태그를 반환해야 함 (하나씩만 매칭되므로 둘 중 하나)
        assert result is not None
        # 어느 것이 반환될지는 데이터베이스 순서에 따라 달라질 수 있으므로
        # 둘 중 하나인지만 확인
        assert result.id in [company_tags[0].id, multi_language_company_tag.id]

    async def test_get_by_names_returns_tag_with_most_matches(
        self, company_tag_repository, async_session
    ):
        # Given
        from app.domain.company_entity import CompanyTagEntity, CompanyTagNameEntity
        from app.dto.company_dto import CompanyTagNameDto

        # 첫 번째 태그: 2개 이름
        tag1_entity = CompanyTagEntity(
            names=(
                CompanyTagNameEntity(language_code="ko", name="태그1"),
                CompanyTagNameEntity(language_code="en", name="tag1"),
            )
        )

        # 두 번째 태그: 3개 이름
        tag2_entity = CompanyTagEntity(
            names=(
                CompanyTagNameEntity(language_code="ko", name="태그2"),
                CompanyTagNameEntity(language_code="en", name="tag2"),
                CompanyTagNameEntity(language_code="ja", name="タグ2"),
            )
        )

        await company_tag_repository.save_all([tag1_entity, tag2_entity])
        await async_session.flush()

        # 검색할 이름들 (tag2가 더 많이 매칭됨)
        names = [
            CompanyTagNameDto(language_code="ko", name="태그1"),  # tag1과 매칭
            CompanyTagNameDto(language_code="ko", name="태그2"),  # tag2와 매칭
            CompanyTagNameDto(language_code="en", name="tag2"),  # tag2와 매칭
            CompanyTagNameDto(language_code="ja", name="タグ2"),  # tag2와 매칭
        ]

        # When
        result = await company_tag_repository.get_by_names(names)

        # Then
        # tag2가 3개 매칭, tag1이 1개 매칭이므로 tag2가 반환되어야 함
        assert result is not None
        assert len(result.names) == 3
        result_names = {name.name for name in result.names}
        assert "태그2" in result_names
        assert "tag2" in result_names
        assert "タグ2" in result_names

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

    async def test_add_missing_names_with_new_language_codes(
        self, company_tag_repository, async_session
    ):
        # Given
        from app.domain.company_entity import CompanyTagEntity, CompanyTagNameEntity
        from app.dto.company_dto import CompanyTagNameDto

        # 기존 태그 생성 (ko, en만 있음)
        tag_entity = CompanyTagEntity(
            names=(
                CompanyTagNameEntity(language_code="ko", name="테스트태그"),
                CompanyTagNameEntity(language_code="en", name="test tag"),
            )
        )

        await company_tag_repository.save_all([tag_entity])
        await async_session.flush()

        # 저장된 태그를 다시 조회해서 실제 ID를 가져옴
        search_names = [CompanyTagNameDto(language_code="ko", name="테스트태그")]
        saved_tag = await company_tag_repository.get_by_names(search_names)
        assert saved_tag is not None
        assert saved_tag.id is not None

        # 새로운 language_code들 추가 (ja, fr)
        names = [
            CompanyTagNameDto(language_code="ko", name="테스트태그"),
            CompanyTagNameDto(language_code="en", name="test tag"),
            CompanyTagNameDto(language_code="ja", name="テストタグ"),
            CompanyTagNameDto(language_code="fr", name="tag de test"),
        ]

        # When
        result = await company_tag_repository.add_missing_names(
            tag=saved_tag, names=names
        )
        await async_session.flush()

        # Then
        assert result is not None
        assert len(result.names) == 4
        result_language_codes = {name.language_code for name in result.names}
        assert result_language_codes == {"ko", "en", "ja", "fr"}

        # 일본어와 프랑스어 이름이 올바르게 추가되었는지 확인
        ja_name = next(name for name in result.names if name.language_code == "ja")
        fr_name = next(name for name in result.names if name.language_code == "fr")
        assert ja_name.name == "テストタグ"
        assert fr_name.name == "tag de test"

    async def test_add_missing_names_with_no_missing_names(
        self, company_tag_repository, async_session
    ):
        # Given
        from app.domain.company_entity import CompanyTagEntity, CompanyTagNameEntity
        from app.dto.company_dto import CompanyTagNameDto

        # 기존 태그 생성
        tag_entity = CompanyTagEntity(
            names=(
                CompanyTagNameEntity(language_code="ko", name="테스트태그"),
                CompanyTagNameEntity(language_code="en", name="test tag"),
            )
        )

        await company_tag_repository.save_all([tag_entity])
        await async_session.flush()

        # 저장된 태그를 다시 조회해서 실제 ID를 가져옴
        search_names = [CompanyTagNameDto(language_code="ko", name="테스트태그")]
        saved_tag = await company_tag_repository.get_by_names(search_names)
        assert saved_tag is not None

        # 동일한 language_code들만 포함
        names = [
            CompanyTagNameDto(language_code="ko", name="테스트태그"),
            CompanyTagNameDto(language_code="en", name="test tag"),
        ]

        # When
        result = await company_tag_repository.add_missing_names(
            tag=saved_tag, names=names
        )

        # Then
        assert result is not None
        assert len(result.names) == 2  # 변화 없음
        result_language_codes = {name.language_code for name in result.names}
        assert result_language_codes == {"ko", "en"}

    async def test_add_missing_names_with_empty_names_list(
        self, company_tag_repository, async_session
    ):
        # Given
        from app.domain.company_entity import CompanyTagEntity, CompanyTagNameEntity
        from app.dto.company_dto import CompanyTagNameDto

        # 기존 태그 생성
        tag_entity = CompanyTagEntity(
            names=(CompanyTagNameEntity(language_code="ko", name="테스트태그"),)
        )

        await company_tag_repository.save_all([tag_entity])
        await async_session.flush()

        # 저장된 태그를 다시 조회해서 실제 ID를 가져옴
        search_names = [CompanyTagNameDto(language_code="ko", name="테스트태그")]
        saved_tag = await company_tag_repository.get_by_names(search_names)
        assert saved_tag is not None

        # When
        result = await company_tag_repository.add_missing_names(tag=saved_tag, names=[])

        # Then
        assert result is not None
        assert len(result.names) == 1  # 변화 없음
        assert result.names[0].language_code == "ko"
