class TestCompanyRepository:
    async def test_get_by_name_not_found(self, company_repository):
        # Given

        # When
        result = await company_repository.get_by_name("없는회사")

        # Then
        assert result is None

    async def test_get_by_name_empty_result(self, company_repository, company):
        # Given

        # When
        result = await company_repository.get_by_name(company.names[0].name + "X")

        # Then
        assert result is None

    async def test_get_by_name_found(self, company_repository, company):
        # Given

        # When
        result = await company_repository.get_by_name(company.names[0].name)

        # Then
        assert result is not None
        assert result.names[0].name == company.names[0].name

    async def test_get_by_partial_name_empty_result(self, company_repository):
        # Given

        # When
        result = await company_repository.get_by_partial_name("없는회사")

        # Then
        assert result == []

    async def test_get_by_partial_name_found_with_exact_match(
        self, company_repository, companies
    ):
        # Given

        # When
        result = await company_repository.get_by_partial_name(
            companies[0].names[0].name
        )

        # Then
        assert len(result) == 1
        assert result[0].names[0].name == companies[0].names[0].name

    async def test_get_by_partial_name_found_with_partial_match_from_start(
        self, company_repository, companies
    ):
        # Given

        # When
        result = await company_repository.get_by_partial_name(
            companies[0].names[0].name[:-1]
        )

        # Then
        assert len(result) == 2
        assert result[0].names[0].name == companies[0].names[0].name
        assert result[1].names[0].name == companies[1].names[0].name

    async def test_get_by_partial_name_found_with_partial_match_from_end(
        self, company_repository, companies
    ):
        # Given

        # When
        result = await company_repository.get_by_partial_name(
            companies[0].names[0].name[1:]
        )

        # Then
        assert len(result) == 1
        assert result[0].names[0].name == companies[0].names[0].name

    async def test_get_by_partial_name_found_with_partial_match_from_middle(
        self, company_repository, companies
    ):
        # Given

        # When
        result = await company_repository.get_by_partial_name(
            companies[0].names[0].name[1:-1]
        )

        # Then
        assert len(result) == 2
        assert result[0].names[0].name == companies[0].names[0].name
        assert result[1].names[0].name == companies[1].names[0].name

    async def test_get_by_tag_empty_result(
        self, company_repository, companies_with_tags
    ):
        # Given

        # When
        result = await company_repository.get_by_tag("없는태그")

        # Then
        assert result == []

    async def test_get_by_tag_empty_result_with_empty_tag(
        self, company_repository, companies_with_tags, company_tags
    ):
        # Given

        # When
        result = await company_repository.get_by_tag(company_tags[2].names[0].name)

        # Then
        assert result == []

    async def test_get_by_tag_found_with_exact_match(
        self, company_repository, companies_with_tags, company_tags
    ):
        # Given

        # When
        result = await company_repository.get_by_tag(company_tags[0].names[0].name)

        # Then
        assert len(result) == 2
        company_names = [company.names[0].name for company in result]
        assert companies_with_tags[0].names[0].name in company_names
        assert companies_with_tags[1].names[0].name in company_names

    async def test_get_by_tag_empty_result_with_partial_match(
        self, company_repository, companies_with_tags, company_tags
    ):
        # Given

        # When
        result = await company_repository.get_by_tag(company_tags[0].names[0].name[:-1])

        # Then
        assert result == []

    async def test_get_by_tag_found_with_case_insensitive_match(
        self, company_repository, companies_with_tags, company_tags
    ):
        # Given

        # When
        result = await company_repository.get_by_tag(company_tags[1].names[0].name)

        # Then
        assert len(result) == 1
        company_names = [company.names[0].name for company in result]
        assert companies_with_tags[2].names[0].name in company_names

    async def test_save_with_names_only(self, company_repository, async_session):
        # Given
        from app.domain.company_entity import CompanyEntity, CompanyNameEntity

        company_entity = CompanyEntity(
            names=(
                CompanyNameEntity(language_code="ko", name="새로운회사"),
                CompanyNameEntity(language_code="en", name="New Company"),
            )
        )

        # When
        await company_repository.save(company_entity)
        await async_session.commit()

        # Then
        company_names = ["새로운회사", "New Company"]
        language_codes = ["ko", "en"]

        saved_company = await company_repository.get_by_name("새로운회사")
        assert saved_company is not None
        assert len(saved_company.names) == 2
        assert saved_company.names[0].name in company_names
        assert saved_company.names[0].language_code in language_codes
        assert saved_company.names[1].name in company_names
        assert saved_company.names[1].language_code in language_codes
        assert len(saved_company.tags) == 0

    async def test_save_with_names_and_tags(self, company_repository, async_session):
        # Given
        from app.domain.company_entity import (
            CompanyEntity,
            CompanyNameEntity,
            CompanyTagEntity,
            CompanyTagNameEntity,
        )

        company_entity = CompanyEntity(
            names=(
                CompanyNameEntity(language_code="ko", name="태그있는회사"),
                CompanyNameEntity(language_code="en", name="Tagged Company"),
            ),
            tags=(
                CompanyTagEntity(
                    names=(
                        CompanyTagNameEntity(language_code="ko", name="태그1"),
                        CompanyTagNameEntity(language_code="en", name="tag1"),
                    )
                ),
                CompanyTagEntity(
                    names=(CompanyTagNameEntity(language_code="ko", name="태그2"),)
                ),
            ),
        )

        # When
        await company_repository.save(company_entity)
        await async_session.commit()

        # Then
        company_names = ["태그있는회사", "Tagged Company"]
        tag_names = ["태그1", "tag1", "태그2"]

        saved_company = await company_repository.get_by_name("태그있는회사")
        assert saved_company is not None
        assert len(saved_company.names) == 2
        assert saved_company.names[0].name in company_names
        assert saved_company.names[1].name in company_names
        assert len(saved_company.tags) == 2
        assert saved_company.tags[0].names[0].name in tag_names
        assert saved_company.tags[0].names[1].name in tag_names
        assert saved_company.tags[1].names[0].name in tag_names

    async def test_save_with_existing_id(self, company_repository, async_session):
        # Given
        from app.domain.company_entity import CompanyEntity, CompanyNameEntity

        existing_id = "12345678-1234-1234-1234-123456789abc"
        company_entity = CompanyEntity(
            id=existing_id,
            names=(CompanyNameEntity(language_code="ko", name="ID있는회사"),),
        )

        # When
        await company_repository.save(company_entity)
        await async_session.commit()

        # Then
        saved_company = await company_repository.get_by_name("ID있는회사")
        assert saved_company is not None
        assert saved_company.id == existing_id
        assert saved_company.names[0].name == "ID있는회사"

    async def test_save_empty_entity(self, company_repository, async_session):
        # Given
        from app.domain.company_entity import CompanyEntity

        company_entity = CompanyEntity(names=(), tags=())

        # When
        await company_repository.save(company_entity)
        await async_session.commit()

        # Then - 빈 entity도 저장될 수 있음
        # 실제로는 비즈니스 로직에서 빈 entity를 저장하지 않도록 해야 함

    # add_tag 메서드 테스트
    async def test_add_tag_to_existing_company(self, company_repository, async_session):
        # Given
        from app.db.models.company_model import Company, CompanyName
        from app.domain.company_entity import CompanyTagEntity, CompanyTagNameEntity

        # 독립적인 회사 생성
        company = Company()
        company.names.append(CompanyName(name="새테스트회사", language_code="ko"))
        async_session.add(company)
        await async_session.flush()

        company_name = "새테스트회사"
        new_tags = [
            CompanyTagEntity(
                names=(
                    CompanyTagNameEntity(language_code="ko", name="새태그1"),
                    CompanyTagNameEntity(language_code="en", name="new tag 1"),
                )
            ),
            CompanyTagEntity(
                names=(CompanyTagNameEntity(language_code="ko", name="새태그2"),)
            ),
        ]

        # When
        result = await company_repository.add_tag(company_name, new_tags)
        await async_session.commit()

        # Then
        assert result is not None
        assert len(result.tags) == 2
        tag_names = [tag.names[0].name for tag in result.tags]
        assert "새태그1" in tag_names
        assert "새태그2" in tag_names

        # DB에서 다시 조회하여 확인
        saved_company = await company_repository.get_by_name(company_name)
        assert saved_company is not None
        assert len(saved_company.tags) == 2

    async def test_add_tag_to_company_with_existing_tags(
        self, company_repository, async_session
    ):
        # Given
        from app.db.models.company_model import (
            Company,
            CompanyName,
            CompanyTag,
            CompanyTagName,
        )
        from app.domain.company_entity import CompanyTagEntity, CompanyTagNameEntity

        # 기존 태그가 있는 회사 생성
        company = Company()
        company.names.append(CompanyName(name="기존태그있는회사", language_code="ko"))

        existing_tag = CompanyTag()
        existing_tag.names.append(CompanyTagName(name="기존태그", language_code="ko"))
        company.tags.append(existing_tag)

        async_session.add(company)
        await async_session.flush()

        company_name = "기존태그있는회사"
        new_tag = [
            CompanyTagEntity(
                names=(CompanyTagNameEntity(language_code="ko", name="추가태그"),)
            )
        ]

        # When
        result = await company_repository.add_tag(company_name, new_tag)
        await async_session.commit()

        # Then
        assert result is not None
        assert len(result.tags) == 2  # 기존 1개 + 추가 1개
        tag_names = [tag.names[0].name for tag in result.tags]
        assert "추가태그" in tag_names
        assert "기존태그" in tag_names

    async def test_add_tag_to_nonexistent_company(self, company_repository):
        # Given
        from app.domain.company_entity import CompanyTagEntity, CompanyTagNameEntity

        nonexistent_company_name = "존재하지않는회사"
        new_tags = [
            CompanyTagEntity(
                names=(CompanyTagNameEntity(language_code="ko", name="태그"),)
            )
        ]

        # When
        result = await company_repository.add_tag(nonexistent_company_name, new_tags)

        # Then
        assert result is None

    async def test_add_empty_tags_list(self, company_repository, async_session):
        # Given
        from app.db.models.company_model import Company, CompanyName

        # 독립적인 회사 생성
        company = Company()
        company.names.append(CompanyName(name="빈태그테스트회사", language_code="ko"))
        async_session.add(company)
        await async_session.flush()

        company_name = "빈태그테스트회사"
        empty_tags = []

        # When
        result = await company_repository.add_tag(company_name, empty_tags)

        # Then
        assert result is not None
        assert len(result.tags) == 0

    # remove_tag 메서드 테스트
    async def test_remove_tag_from_company_with_tags(
        self, company_repository, async_session
    ):
        # Given
        from app.db.models.company_model import (
            Company,
            CompanyName,
            CompanyTag,
            CompanyTagName,
        )

        # 태그가 있는 회사 생성 (고유한 이름 사용)
        company = Company()
        company.names.append(CompanyName(name="제거테스트회사", language_code="ko"))

        tag = CompanyTag()
        tag.names.append(CompanyTagName(name="제거할태그", language_code="ko"))

        company.tags.append(tag)
        async_session.add(company)
        await async_session.flush()

        company_name = "제거테스트회사"
        tag_to_remove = "제거할태그"

        # When
        result = await company_repository.remove_tag(company_name, tag_to_remove)
        await async_session.commit()

        # Then
        assert result is not None
        assert len(result.tags) == 0  # 태그가 제거되어 0개가 됨

        # DB에서 다시 조회하여 확인
        saved_company = await company_repository.get_by_name(company_name)
        assert saved_company is not None
        assert len(saved_company.tags) == 0

    async def test_remove_tag_from_company_with_multiple_tags(
        self, company_repository, async_session
    ):
        # Given
        from app.db.models.company_model import (
            Company,
            CompanyName,
            CompanyTag,
            CompanyTagName,
        )

        # 여러 태그를 가진 회사 생성
        company = Company()
        company.names.append(CompanyName(name="다중태그회사", language_code="ko"))

        tag1 = CompanyTag()
        tag1.names.append(CompanyTagName(name="태그A", language_code="ko"))
        tag2 = CompanyTag()
        tag2.names.append(CompanyTagName(name="태그B", language_code="ko"))

        company.tags.extend([tag1, tag2])
        async_session.add(company)
        await async_session.flush()

        company_name = "다중태그회사"
        tag_to_remove = "태그A"

        # When
        result = await company_repository.remove_tag(company_name, tag_to_remove)
        await async_session.commit()

        # Then
        assert result is not None
        assert len(result.tags) == 1
        assert result.tags[0].names[0].name == "태그B"

    async def test_remove_nonexistent_tag_from_company(
        self, company_repository, async_session
    ):
        # Given
        from app.db.models.company_model import (
            Company,
            CompanyName,
            CompanyTag,
            CompanyTagName,
        )

        # 태그가 있는 회사 생성
        company = Company()
        company.names.append(CompanyName(name="기존태그회사", language_code="ko"))

        tag = CompanyTag()
        tag.names.append(CompanyTagName(name="기존태그", language_code="ko"))

        company.tags.append(tag)
        async_session.add(company)
        await async_session.flush()

        company_name = "기존태그회사"
        nonexistent_tag = "존재하지않는태그"

        # When
        result = await company_repository.remove_tag(company_name, nonexistent_tag)

        # Then
        assert result is not None
        assert len(result.tags) == 1  # 기존 태그는 그대로 유지

    async def test_remove_tag_from_nonexistent_company(self, company_repository):
        # Given
        nonexistent_company_name = "존재하지않는회사"
        tag_name = "태그"

        # When
        result = await company_repository.remove_tag(nonexistent_company_name, tag_name)

        # Then
        assert result is None

    async def test_remove_tag_from_company_without_tags(
        self, company_repository, async_session
    ):
        # Given
        from app.db.models.company_model import Company, CompanyName

        # 태그가 없는 회사 생성
        company = Company()
        company.names.append(CompanyName(name="태그없는회사", language_code="ko"))
        async_session.add(company)
        await async_session.flush()

        company_name = "태그없는회사"
        tag_name = "태그"

        # When
        result = await company_repository.remove_tag(company_name, tag_name)

        # Then
        assert result is not None
        assert len(result.tags) == 0

    # 캐시 무효화 테스트
    async def test_add_tag_invalidates_cache(
        self, company_repository, redis_client, async_session
    ):
        # Given
        from app.db.models.company_model import Company, CompanyName
        from app.domain.company_entity import CompanyTagEntity, CompanyTagNameEntity

        # 회사 생성
        company = Company()
        company.names.append(CompanyName(name="캐시테스트회사", language_code="ko"))
        async_session.add(company)
        await async_session.flush()

        company_name = "캐시테스트회사"
        new_tag = [
            CompanyTagEntity(
                names=(CompanyTagNameEntity(language_code="ko", name="캐시테스트태그"),)
            )
        ]

        # 캐시에 회사 정보 저장
        await company_repository.get_by_name(company_name)
        cache_key = f"repository:company:name:{company_name}"
        assert await redis_client.exists(cache_key) == 1

        # When
        await company_repository.add_tag(company_name, new_tag)

        # Then
        assert await redis_client.exists(cache_key) == 0  # 캐시가 무효화됨

    async def test_remove_tag_invalidates_cache(
        self, company_repository, redis_client, async_session
    ):
        # Given
        from app.db.models.company_model import (
            Company,
            CompanyName,
            CompanyTag,
            CompanyTagName,
        )

        # 태그가 있는 회사 생성
        company = Company()
        company.names.append(CompanyName(name="캐시제거테스트회사", language_code="ko"))

        tag = CompanyTag()
        tag.names.append(CompanyTagName(name="캐시제거태그", language_code="ko"))

        company.tags.append(tag)
        async_session.add(company)
        await async_session.flush()

        company_name = "캐시제거테스트회사"
        tag_to_remove = "캐시제거태그"

        # 캐시에 회사 정보 저장
        await company_repository.get_by_name(company_name)
        cache_key = f"repository:company:name:{company_name}"
        assert await redis_client.exists(cache_key) == 1

        # When
        await company_repository.remove_tag(company_name, tag_to_remove)

        # Then
        assert await redis_client.exists(cache_key) == 0  # 캐시가 무효화됨
