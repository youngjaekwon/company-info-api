class TestCompanyNameAutocomplete:
    """
    1. 회사명 자동완성
    회사명의 일부만 들어가도 검색이 되어야 합니다.
    header의 x-wanted-language 언어값에 따라 해당 언어로 출력되어야 합니다.
    """

    def test_company_name_autocomplete(self, fastapi_client, setup_company_test_data):
        response = fastapi_client.get(
            "/search?query=링크", headers={"x-wanted-language": "ko"}
        )

        assert response.status_code == 200
        searched_companies = response.json()

        assert searched_companies == [
            {"company_name": "주식회사 링크드코리아"},
            {"company_name": "스피링크"},
        ]


class TestCompanySearch:
    """
    2. 회사 이름으로 회사 검색
    header의 x-wanted-language 언어값에 따라 해당 언어로 출력되어야 합니다.
    """

    def test_company_search(self, fastapi_client, setup_company_test_data):
        response = fastapi_client.get(
            "/companies/Wantedlab", headers={"x-wanted-language": "ko"}
        )

        assert response.status_code == 200
        company = response.json()

        assert company == {
            "company_name": "원티드랩",
            "tags": [
                "태그_4",
                "태그_20",
                "태그_16",
            ],
        }

    def test_company_search_not_found(self, fastapi_client, setup_company_test_data):
        # 검색된 회사가 없는경우 404를 리턴합니다.
        response = fastapi_client.get(
            "/companies/없는회사", headers={"x-wanted-language": "ko"}
        )

        assert response.status_code == 404


class TestNewCompany:
    """
    3. 새로운 회사 추가
    새로운 언어(tw)도 같이 추가 될 수 있습니다.
    저장 완료후 header의 x-wanted-language 언어값에 따라 해당 언어로 출력되어야 합니다.
    """

    def test_new_company(self, fastapi_client, setup_company_test_data):
        response = fastapi_client.post(
            "/companies",
            json={
                "company_name": {
                    "ko": "라인 프레쉬",
                    "tw": "LINE FRESH",
                    "en": "LINE FRESH",
                },
                "tags": [
                    {
                        "tag_name": {
                            "ko": "태그_1",
                            "tw": "tag_1",
                            "en": "tag_1",
                        }
                    },
                    {
                        "tag_name": {
                            "ko": "태그_8",
                            "tw": "tag_8",
                            "en": "tag_8",
                        }
                    },
                    {
                        "tag_name": {
                            "ko": "태그_15",
                            "tw": "tag_15",
                            "en": "tag_15",
                        }
                    },
                ],
            },
            headers={"x-wanted-language": "tw"},
        )

        company = response.json()
        assert company == {
            "company_name": "LINE FRESH",
            "tags": [
                "tag_1",
                "tag_8",
                "tag_15",
            ],
        }


class TestSearchTagName:
    """
    4. 태그명으로 회사 검색
    태그로 검색 관련된 회사가 검색되어야 합니다.
    다국어로 검색이 가능해야 합니다.
    일본어 태그로 검색을 해도 language가 ko이면 한국 회사명이 노출이 되어야 합니다.
    ko언어가 없을경우 노출가능한 언어로 출력합니다.
    동일한 회사는 한번만 노출이 되어야합니다.
    """

    def test_search_tag_name(self, fastapi_client, setup_company_test_data):
        response = fastapi_client.get(
            "/tags?query=タグ_22", headers={"x-wanted-language": "ko"}
        )

        searched_companies = response.json()

        assert [company["company_name"] for company in searched_companies] == [
            "딤딤섬 대구점",
            "마이셀럽스",
            "Rejoice Pregnancy",
            "삼일제약",
            "투게더앱스",
        ]


class TestNewTag:
    """
    5. 회사 태그 정보 추가
    저장 완료후 header의 x-wanted-language 언어값에 따라 해당 언어로 출력되어야 합니다.
    """

    def test_new_tag(self, fastapi_client, setup_company_test_data):
        response = fastapi_client.put(
            "/companies/원티드랩/tags",
            json=[
                {
                    "tag_name": {
                        "ko": "태그_50",
                        "jp": "タグ_50",
                        "en": "tag_50",
                    }
                },
                {
                    "tag_name": {
                        "ko": "태그_4",
                        "tw": "tag_4",
                        "en": "tag_4",
                    }
                },
            ],
            headers={"x-wanted-language": "en"},
        )

        company = response.json()
        assert company == {
            "company_name": "Wantedlab",
            "tags": [
                "tag_4",
                "tag_20",
                "tag_16",
                "tag_50",
            ],
        }


class TestDeleteTag:
    """
    6. 회사 태그 정보 삭제
    저장 완료후 header의 x-wanted-language 언어값에 따라 해당 언어로 출력되어야 합니다.
    """

    def test_delete_tag(self, fastapi_client, setup_company_test_data):
        # 먼저 태그를 추가한 상태에서 삭제 테스트
        # test_new_tag가 실행된 후 상태를 가정
        fastapi_client.put(
            "/companies/원티드랩/tags",
            json=[
                {
                    "tag_name": {
                        "ko": "태그_50",
                        "jp": "タグ_50",
                        "en": "tag_50",
                    }
                },
                {
                    "tag_name": {
                        "ko": "태그_4",
                        "tw": "tag_4",
                        "en": "tag_4",
                    }
                },
            ],
            headers={"x-wanted-language": "en"},
        )

        # 태그 삭제
        response = fastapi_client.delete(
            "/companies/원티드랩/tags/태그_16",
            headers={"x-wanted-language": "en"},
        )

        company = response.json()
        assert company == {
            "company_name": "Wantedlab",
            "tags": [
                "tag_4",
                "tag_20",
                "tag_50",
            ],
        }
