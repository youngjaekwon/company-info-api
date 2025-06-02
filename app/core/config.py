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


settings = Settings()