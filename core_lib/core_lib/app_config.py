from enum import Enum
from os import getenv


class Environment(Enum):
    LOCALHOST = "LOCALHOST"
    PRODUCTION = "PRODUCTION"


class AppConfig:

    _environment: Environment = Environment(getenv("ENVIRONMENT", "LOCALHOST"))

    @staticmethod
    def _required_env(variable_name: str) -> str:
        value = getenv(variable_name)
        if value is None:
            raise Exception(f"Required environment variable {variable_name} is missing")
        return value

    @staticmethod
    def is_production() -> bool:
        return AppConfig._environment == Environment.PRODUCTION

    @staticmethod
    def is_localhost() -> bool:
        return AppConfig._environment == Environment.LOCALHOST

    @staticmethod
    def sentry_dsn() -> str:
        return AppConfig._required_env("SENTRY_DSN")

    @staticmethod
    def token_secret_key() -> str:
        return AppConfig._required_env("TOKEN_SECRET")

    @staticmethod
    def environment() -> str:
        return AppConfig._environment.value
