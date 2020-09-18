from enum import Enum
from os import getenv


class Environment(Enum):
    LOCALHOST = "LOCALHOST"
    PRODUCTION = "PRODUCTION"


class AppConfig:

    _environment: Environment = Environment(getenv("ENVIRONMENT", "LOCALHOST"))

    @staticmethod
    def is_production() -> bool:
        return AppConfig._environment == Environment.PRODUCTION

    @staticmethod
    def is_localhost() -> bool:
        return AppConfig._environment == Environment.LOCALHOST
