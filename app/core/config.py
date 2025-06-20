from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.constants import EnvConstants, get_env_file


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=get_env_file(),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ENV: str = EnvConstants.DEV

    # Database settings
    DATABASE_URL: str
    DATABASE_SCHEMA: str = "public"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_POOL_RECYCLE: int = 1800
    SQLALCHEMY_ECHO: bool = False

    # Redis settings
    REDIS_URL: str
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str
    REDIS_MAX_CONNECTIONS: int = 100

    # Cache settings
    REPOSITORY_CACHE_TTL: int = 60 * 60 * 12  # 12 hours
    REPOSITORY_CACHE_PARTIAL_TTL: int = 60  # 1 minute, 부분 검색용 캐시 TTL


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
