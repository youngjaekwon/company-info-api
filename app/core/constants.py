import os
from pathlib import Path

ROOT_PATH = Path(__file__).resolve().parents[2]
ENV_DIR = os.path.join(ROOT_PATH, "envs")


class EnvConstants:
    DEV = "dev"
    TEST = "test"
    PROD = "prod"


def get_env_file(env: EnvConstants | None = None) -> str:
    if env is None:
        env = os.getenv("APP_ENV", EnvConstants.DEV)

    return os.path.join(ENV_DIR, f".env.{env}")
