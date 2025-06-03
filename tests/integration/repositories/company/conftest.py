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
def company_repository(async_session, company_mapper, redis_client, settings):
    from app.repositories.company_repository import CompanyRepository

    return CompanyRepository(
        db=async_session,
        company_mapper=company_mapper,
        redis_client=redis_client,
        settings=settings,
    )


@pytest.fixture()
def company_tag_repository(async_session, company_tag_mapper):
    from app.repositories.company_tag_repository import CompanyTagRepository

    return CompanyTagRepository(
        db=async_session,
        company_tag_mapper=company_tag_mapper,
    )


@pytest.fixture
async def company(async_session):
    from app.db.models.company_model import Company, CompanyName

    test_company_name = "테스트회사"
    company = Company()
    company.names.append(CompanyName(name=test_company_name, language_code="ko"))
    async_session.add(company)
    await async_session.flush()
    return company


@pytest.fixture
async def companies(async_session):
    from app.db.models.company_model import Company, CompanyName

    company_names = ["회사1", "회사2", "기업1"]
    companies = []
    for name in company_names:
        company = Company()
        company.names.append(CompanyName(name=name, language_code="ko"))
        async_session.add(company)
        companies.append(company)
    await async_session.flush()
    return companies


@pytest.fixture
async def company_tags(async_session):
    from app.db.models.company_model import CompanyTag, CompanyTagName

    tag1 = CompanyTag()
    tag1.names.append(CompanyTagName(name="태그1", language_code="ko"))

    tag2 = CompanyTag()
    tag2.names.append(CompanyTagName(name="태그2", language_code="ko"))

    tag3 = CompanyTag()
    tag3.names.append(CompanyTagName(name="태그3", language_code="ko"))

    async_session.add_all([tag1, tag2, tag3])
    await async_session.flush()
    return [tag1, tag2, tag3]


@pytest.fixture
async def companies_with_tags(async_session, companies, company_tags):
    from app.db.models.company_model import company_tag

    await async_session.execute(
        company_tag.insert(),
        [
            {"company_id": companies[0].id, "company_tag_id": company_tags[0].id},
            {"company_id": companies[1].id, "company_tag_id": company_tags[0].id},
            {"company_id": companies[2].id, "company_tag_id": company_tags[1].id},
        ],
    )

    return companies


@pytest.fixture
async def multi_language_company_tag(async_session):
    from app.db.models.company_model import CompanyTag, CompanyTagName

    tag = CompanyTag()
    tag.names.append(CompanyTagName(name="다국어태그", language_code="ko"))
    tag.names.append(CompanyTagName(name="multilingual tag", language_code="en"))
    tag.names.append(CompanyTagName(name="多言語タグ", language_code="jp"))
    async_session.add(tag)
    await async_session.flush()
    return tag
