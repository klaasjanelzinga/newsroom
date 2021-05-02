from enum import Enum
from os import getenv
from typing import Optional
from urllib.parse import quote_plus


class Environment(Enum):
    LOCALHOST = "localhost"
    PRODUCTION = "production"


class AppConfig:
    @staticmethod
    def _required_env(variable_name: str) -> str:
        value = getenv(variable_name)
        if value is None:
            raise Exception(f"Required environment variable {variable_name} is missing")
        return value

    @staticmethod
    def is_production() -> bool:
        return AppConfig.environment() == Environment.PRODUCTION

    @staticmethod
    def is_localhost() -> bool:
        return AppConfig.environment() == Environment.LOCALHOST

    @staticmethod
    def sentry_dsn_api() -> Optional[str]:
        return getenv("SENTRY_DSN_API")

    @staticmethod
    def sentry_dsn_cron() -> Optional[str]:
        return getenv("SENTRY_DSN_CRON")

    @staticmethod
    def token_secret_key() -> str:
        return AppConfig._required_env("TOKEN_SECRET")

    @staticmethod
    def environment() -> str:
        return AppConfig._required_env("ENVIRONMENT")

    @staticmethod
    def mongodb_url() -> str:
        mongo_user = AppConfig._required_env("MONGO_USER")
        mongo_pass = AppConfig._required_env("MONGO_PASS")
        mongo_host = AppConfig._required_env("MONGO_HOST")
        mongo_port = AppConfig._required_env("MONGO_PORT")
        mongo_db = AppConfig.mongo_db()
        return f"mongodb://{quote_plus(mongo_user)}:{quote_plus(mongo_pass)}@{mongo_host}:{mongo_port}/{mongo_db}"

    @staticmethod
    def mongo_db() -> str:
        return AppConfig._required_env("MONGO_DB")
