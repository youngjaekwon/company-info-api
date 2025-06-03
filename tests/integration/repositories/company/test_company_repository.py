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
