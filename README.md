# Company Info API

## Summary

회사 정보 관리 시스템 API입니다.  
회사 정보를 생성, 조회, 검색할 수 있으며, 각 회사에 태그를 추가하거나 삭제할 수 있습니다.  
다국어를 지원하여 한국어와 영어 등으로 회사명과 태그를 관리할 수 있습니다.

---

## 기능 설명

### 회사 (Company)

- 회사 생성 및 조회
- 다국어 회사명 지원 (한국어, 영어 등)
- 회사명 부분 검색 기능
- 회사별 태그 관리

### 태그 (CompanyTag)

- 회사에 태그 추가/삭제 기능
- 다국어 태그명 지원 (한국어, 영어 등)
- 태그별 회사 검색 기능

### 검색 기능

- 회사명 부분 검색
- 회사명으로 회사 검색
- 태그로 회사 검색
- 언어별 검색 결과 제공

---

## 기술 스택

- **Backend**: FastAPI (Python 3.12+)
- **Database**: PostgreSQL 14
- **Cache**: Redis 7
- **ORM**: SQLAlchemy
- **Migration**: Alembic
- **Dependency Management**: uv
- **Container**: Docker & Docker Compose
- **Testing**: pytest, pytest-asyncio

---

## 실행 방법 (Docker Compose)

### 환경 변수 설정

Docker Compose를 사용하기 전에 필요한 환경변수를 설정해주세요:

```bash
cp ./envs/.env.prod.example ./envs/.env.prod
```

### 실행

```bash
# Windows
docker-compose --env-file ./env/.env.prod up -d --build

# Linux/MacOS
docker compose --env-file ./env/.env.prod up -d --build
```

웹 서버는 기본적으로 `http://localhost:8000`에서 실행됩니다.

---

## API 문서

### Swagger UI

Swagger UI 문서는 아래 주소에서 확인 가능합니다:

```
http://localhost:8000/docs
```

### ReDoc

ReDoc 문서는 아래 주소에서 확인 가능합니다:

```
http://localhost:8000/redoc
```

---

## 로컬 실행 방법

### Python 버전 요구사항

- Python 3.12 이상

### 데이터베이스 요구사항

- PostgreSQL 5432 port로 실행
- Redis 6379 port로 실행

### uv 사용 (권장)

```bash
# 의존성 설치
uv sync

# 데이터베이스 마이그레이션
uv run alembic upgrade head

# 서버 실행
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### pip 사용

```bash
# 의존성 설치
pip install -e .

# 데이터베이스 마이그레이션
alembic upgrade head

# 서버 실행
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 테스트 방법

### uv 사용

```bash
# 모든 테스트 실행
uv run pytest

# 통합 테스트만 실행
uv run pytest -m integration

# E2E 테스트만 실행
uv run pytest tests/e2e/
```

### pip 사용

```bash
# 모든 테스트 실행
pytest

# 통합 테스트만 실행
pytest -m integration

# E2E 테스트만 실행
pytest tests/e2e/
```

---

## API 엔드포인트

### 회사 검색

```
GET /search?query={검색어}
```

### 회사 생성

```
POST /companies
```

### 회사 조회

```
GET /companies/{회사명}
```

### 회사 태그 추가

```
PUT /companies/{회사명}/tags
```

### 회사 태그 삭제

```
DELETE /companies/{회사명}/tags/{태그명}
```

### 태그로 회사 검색

```
GET /tags?query={태그명}
```

---

## 디렉터리 구조

```
.
├── app/                     # 애플리케이션 소스 코드
│   ├── api/                 # API 라우터 및 엔드포인트
│   │   └── v1/              # API v1
│   ├── containers/          # 의존성 주입 컨테이너
│   ├── core/                # 핵심 설정 및 공통 기능
│   ├── db/                  # 데이터베이스 설정
│   ├── domain/              # 도메인 엔티티
│   ├── dto/                 # 데이터 전송 객체
│   ├── interfaces/          # 인터페이스 정의
│   ├── mappers/             # 데이터 매핑
│   ├── repositories/        # 데이터 액세스 레이어
│   ├── schemas/             # Pydantic 스키마
│   ├── services/            # 비즈니스 로직
│   └── main.py              # FastAPI 애플리케이션 엔트리포인트
├── tests/                   # 테스트 코드
│   ├── e2e/                 # E2E 테스트
│   ├── integration/         # 통합 테스트
│   └── conftest.py          # 테스트 설정
├── alembic.ini              # Alembic 설정
├── docker-compose.yml       # Docker Compose 설정
├── Dockerfile               # Docker 이미지 설정
├── entrypoint.sh            # 컨테이너 엔트리포인트
├── pyproject.toml           # Python 프로젝트 설정
├── company_tag_sample.csv   # 샘플 데이터
└── uv.lock                  # 의존성 잠금 파일
```
