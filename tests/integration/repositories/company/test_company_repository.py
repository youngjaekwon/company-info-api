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

        company_entity = CompanyEntity()

        # When
        await company_repository.save(company_entity)
        await async_session.commit()

        # Then
        await async_session.flush()
