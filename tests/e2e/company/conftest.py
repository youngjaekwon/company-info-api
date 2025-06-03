import csv
from pathlib import Path

import pytest
from sqlalchemy import insert


@pytest.fixture()
async def setup_company_test_data(async_session):
    """CSV 파일에서 회사와 태그 데이터를 라인별로 순차적으로 읽어서 테스트 데이터 셋업"""
    from app.db.models import (
        Company,
        CompanyName,
        CompanyTag,
        CompanyTagName,
        company_tag,
    )

    # CSV 파일 경로 설정
    csv_file_path = (
        Path(__file__).parent.parent.parent.parent / "company_tag_sample.csv"
    )

    if not csv_file_path.exists():
        raise FileNotFoundError(f"CSV 파일을 찾을 수 없습니다: {csv_file_path}")

    # 태그 캐시 (중복 방지용)
    tag_cache = {}  # (ko, en, jp, tw) -> CompanyTag 객체
    created_companies = []
    created_tags = []

    # CSV 파일을 라인별로 순차 처리
    with open(csv_file_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row_idx, row in enumerate(reader, 1):
            # 회사명 정보 추출
            company_ko = row["company_ko"].strip() if row["company_ko"] else None
            company_en = row["company_en"].strip() if row["company_en"] else None
            company_ja = row["company_ja"].strip() if row["company_ja"] else None

            # 회사명이 모두 빈 값이면 스킵
            if not any([company_ko, company_en, company_ja]):
                continue

            # 1. 회사 생성
            company = Company()
            async_session.add(company)
            await async_session.flush()  # ID를 받기 위해
            created_companies.append(company)

            # 회사명들 추가
            company_names_data = [
                ("ko", company_ko),
                ("en", company_en),
                ("jp", company_ja),
            ]

            for lang, name in company_names_data:
                if name:  # 빈 문자열이 아닌 경우만 추가
                    company_name = CompanyName(
                        company_id=company.id, language_code=lang, name=name
                    )
                    async_session.add(company_name)

            # 2. 태그 정보 파싱 및 생성
            tag_ko_list = row["tag_ko"].split("|") if row["tag_ko"] else []
            tag_en_list = row["tag_en"].split("|") if row["tag_en"] else []
            tag_ja_list = row["tag_ja"].split("|") if row["tag_ja"] else []

            # 태그 길이 맞추기 (가장 긴 것을 기준으로)
            max_len = max(len(tag_ko_list), len(tag_en_list), len(tag_ja_list), 1)
            tag_ko_list.extend([""] * (max_len - len(tag_ko_list)))
            tag_en_list.extend([""] * (max_len - len(tag_en_list)))
            tag_ja_list.extend([""] * (max_len - len(tag_ja_list)))

            # 3. 각 태그 처리 및 회사-태그 관계 설정
            company_tag_relations = []

            for i in range(max_len):
                tag_ko = tag_ko_list[i].strip() if tag_ko_list[i] else ""
                tag_en = tag_en_list[i].strip() if tag_en_list[i] else ""
                tag_ja = tag_ja_list[i].strip() if tag_ja_list[i] else ""

                # 모든 태그명이 비어있으면 스킵
                if not any([tag_ko, tag_en, tag_ja]):
                    continue

                tag_key = (tag_ko, tag_en, tag_ja)

                # 태그가 이미 생성되었는지 확인
                if tag_key in tag_cache:
                    tag = tag_cache[tag_key]
                else:
                    # 새 태그 생성
                    tag = CompanyTag()
                    async_session.add(tag)
                    await async_session.flush()  # ID를 받기 위해
                    created_tags.append(tag)
                    tag_cache[tag_key] = tag

                    # 태그명들 추가
                    tag_names_data = [
                        ("ko", tag_ko),
                        ("en", tag_en),
                        ("jp", tag_ja),
                    ]

                    for lang, name in tag_names_data:
                        if name:  # 빈 문자열이 아닌 경우만 추가
                            tag_name = CompanyTagName(
                                company_tag_id=tag.id, language_code=lang, name=name
                            )
                            async_session.add(tag_name)

                # 회사-태그 관계 추가
                company_tag_relations.append(
                    {"company_id": company.id, "company_tag_id": tag.id}
                )

            # 4. 해당 회사의 태그 관계들 DB에 저장
            if company_tag_relations:
                await async_session.execute(insert(company_tag), company_tag_relations)

            # 각 라인 처리 후 커밋
            await async_session.commit()

    # 데이터 반환 (테스트에서 사용할 수 있도록)
    return {
        "companies": created_companies,
        "tags": created_tags,
    }
