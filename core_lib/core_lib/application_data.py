import logging
import os
from typing import List
from unittest.mock import MagicMock, Mock, AsyncMock  # type: ignore

from aiohttp import ClientSession, ClientResponse
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

    def mock_client_session_for_files(self, file_names: List[str]) -> ClientSession:
        def _response_for_file(file_name: str) -> AsyncMock:
            with open(file_name) as file:
                read_in_file = file.read()
                text_response = AsyncMock(ClientResponse)
                text_response.text.return_value = read_in_file

                response = Mock()
                response.__aenter__ = AsyncMock(return_value=text_response)
                response.__aexit__ = AsyncMock(return_value=None)
                return response

        client_session = AsyncMock(ClientSession)
        client_session.get.side_effect = [_response_for_file(file_name) for file_name in file_names]
        self.client_session = client_session
        return client_session

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

    def feed(self) -> FeedRepository:
        return self.feed_repository

    def feed_item(self) -> FeedItemRepository:
        return self.feed_item_repository

    def news_item(self) -> NewsItemRepository:
        return self.news_item_repository

    def user(self) -> UserRepository:
        return self.user_repository

    def reset_mocks(self) -> None:
        self.client.reset_mock()
        self.mock_user_repository().reset_mock()
        self.mock_news_item_repository().reset_mock()
        self.mock_feed_item_repository().reset_mock()
        self.mock_feed_repository().reset_mock()
        self.mock_subscription_repository().reset_mock()
        self.mock_client_session().reset_mock()


repositories = Repositories()
