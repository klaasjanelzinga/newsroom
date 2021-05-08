import logging
from typing import Optional

from aiohttp import ClientSession
from motor.motor_asyncio import AsyncIOMotorClient

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
    def __init__(self, client: AsyncIOMotorClient, mongodb_db: str, client_session: ClientSession) -> None:
        log.info("Initializing repositories.")
        self.mongo_client = client
        self.database = self.mongo_client.get_database(mongodb_db)
        self.user_repository = UserRepository(self.database)
        self.news_item_repository = NewsItemRepository(self.database)
        self.saved_news_item_repository = SavedNewsItemRepository(self.database)
        self.feed_item_repository = FeedItemRepository(self.database)
        self.feed_repository = FeedRepository(self.database)
        self.client_session = client_session


_repositories: Optional[Repositories] = None


def repositories() -> Repositories:
    if _repositories is None:
        raise Exception("Initialization error")
    return _repositories
