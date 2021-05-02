import logging
import os

from aiohttp import ClientSession, ClientTimeout
from motor.motor_asyncio import AsyncIOMotorClient

from core_lib.app_config import AppConfig
from core_lib.repositories import (
    FeedItemRepository,
    FeedRepository,
    NewsItemRepository,
    SavedNewsItemRepository,
    UserRepository,
)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__file__)


class Repositories:
    @staticmethod
    def not_in_unit_tests() -> bool:
        return "unit_tests" not in os.environ

    def __init__(self) -> None:
        log.info("Initializing repositories.")
        self.client = AsyncIOMotorClient(AppConfig.mongodb_url())
        self.database = self.client.get_database(AppConfig.mongo_db())
        self.user_repository = UserRepository(self.database)
        self.news_item_repository = NewsItemRepository(self.database)
        self.saved_news_item_repository = SavedNewsItemRepository(self.database)
        self.feed_item_repository = FeedItemRepository(self.database)
        self.feed_repository = FeedRepository(self.database)
        timeout = ClientTimeout(total=290)
        self.client_session = ClientSession(timeout=timeout)


repositories: Repositories = Repositories() if Repositories.not_in_unit_tests() else None  # type: ignore
