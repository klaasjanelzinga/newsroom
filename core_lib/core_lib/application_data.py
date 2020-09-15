import logging
import os
from unittest.mock import MagicMock

from aiohttp import ClientSession
from google.cloud import datastore
from google.cloud.datastore import Client

from core_lib.repositories import (
    FeedRepository,
    SubscriptionRepository,
    FeedItemRepository,
    NewsItemRepository,
    UserRepository,
)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__file__)


class Repositories:
    @staticmethod
    def not_in_unit_tests() -> bool:
        return "unit_tests" not in os.environ

    def __init__(self) -> None:
        if Repositories.not_in_unit_tests():
            self.client = datastore.Client()
            self.user_repository = UserRepository(self.client)
            self.news_item_repository = NewsItemRepository(self.client)
            self.feed_item_repository = FeedItemRepository(self.client)
            self.feed_repository = FeedRepository(self.client)
            self.subscription_repository = SubscriptionRepository(self.client)
            self.client_session = ClientSession()
        else:
            self.client = MagicMock(Client)
            self.user_repository = MagicMock(UserRepository)
            self.news_item_repository = MagicMock(NewsItemRepository)  # type: ignore
            self.feed_item_repository = MagicMock(FeedItemRepository)  # type: ignore
            self.feed_repository = MagicMock(FeedRepository)  # type: ignore
            self.subscription_repository = MagicMock(SubscriptionRepository)  # type: ignore
            self.client_session = MagicMock(ClientSession)  # type: ignore

    def mock_user_repository(self) -> MagicMock:
        return self.user_repository  # type: ignore

    def mock_subscription_repository(self) -> MagicMock:
        return self.subscription_repository  # type: ignore

    def mock_news_item_repository(self) -> MagicMock:
        return self.news_item_repository  # type: ignore

    def mock_feed_item_repository(self) -> MagicMock:
        return self.feed_item_repository  # type: ignore

    def mock_feed_repository(self) -> MagicMock:
        return self.feed_repository  # type: ignore

    def mock_client_session(self) -> MagicMock:
        return self.client_session  # type: ignore

    def reset_mocks(self) -> None:
        self.client.reset_mock()
        self.mock_user_repository().reset_mock()
        self.mock_news_item_repository().reset_mock()
        self.mock_feed_item_repository().reset_mock()
        self.mock_feed_repository().reset_mock()
        self.mock_subscription_repository().reset_mock()
        self.mock_client_session().reset_mock()


repositories = Repositories()
