import logging
import os

from aiohttp import ClientSession, ClientTimeout
from google.cloud import datastore

from core_lib.gemeente_groningen import feed_gemeente_groningen, gemeente_groningen_parser
from core_lib.repositories import (
    FeedItemRepository,
    FeedRepository,
    NewsItemRepository,
    SavedNewsItemRepository,
    SubscriptionRepository,
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
        self.client = datastore.Client()
        self.user_repository = UserRepository(self.client)
        self.news_item_repository = NewsItemRepository(self.client)
        self.saved_news_item_repository = SavedNewsItemRepository(self.client)
        self.feed_item_repository = FeedItemRepository(self.client)
        self.feed_repository = FeedRepository(self.client)
        self.subscription_repository = SubscriptionRepository(self.client)
        timeout = ClientTimeout(total=290)
        self.client_session = ClientSession(timeout=timeout)


repositories: Repositories = Repositories() if Repositories.not_in_unit_tests() else None  # type: ignore
html_feeds = [feed_gemeente_groningen]
html_feed_parsers = {
    feed_gemeente_groningen.feed_id: gemeente_groningen_parser,
}
