import logging
from typing import Optional, List, Tuple, Dict
from unittest.mock import MagicMock, AsyncMock, Mock

from aiohttp import ClientSession, ClientResponse
from google.cloud.datastore import Client

from core_lib.gemeente_groningen import feed_gemeente_groningen
from core_lib.repositories import Feed, Subscription, User, FeedItem, NewsItem


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__file__)


class FeedRepository:
    def __init__(self):
        self.store: Dict[str, Feed] = {}

    def reset(self):
        self.store = {}

    def count(self) -> int:
        return len(self.store)

    def find_by_url(self, url: str) -> Optional[Feed]:
        feeds = [feed for feed in self.store.values() if feed.url == url]
        if len(feeds) != 1:
            return None
        return feeds[0]

    def upsert(self, feed: Feed) -> Feed:
        self.store[feed.feed_id] = feed
        return feed

    def all_feeds(self) -> List[Feed]:
        return self.store.values()

    def get(self, feed_id: str) -> Feed:
        feed = self.store.get(feed_id)
        if feed is None:
            raise Exception(f"Feed with id {feed_id} not found.")
        return feed

    def get_active_feeds(self) -> List[Feed]:
        return [feed for feed in self.store.values() if feed.number_of_subscriptions > 0]


class SubscriptionRepository:
    def __init__(self):
        self.store: Dict[str, Subscription] = {}

    def reset(self):
        self.store = {}

    def count(self) -> int:
        return len(self.store)

    def upsert(self, subscription: Subscription) -> Subscription:
        self.store[subscription.subscription_id] = subscription
        return subscription

    def delete_user_feed(self, user: User, feed: Feed) -> None:
        keys = [
            sub.subscription_id
            for sub in self.store.values()
            if sub.user_id == user.user_id and sub.feed_id == feed.feed_id
        ]
        for key in keys:
            del self.store[key]


class FeedItemRepository:
    def __init__(self):
        self.store: Dict[str, FeedItem] = {}

    def reset(self):
        self.store = {}

    def count(self) -> int:
        return len(self.store)

    def fetch_all_for_feed(self, feed: Feed) -> List[FeedItem]:
        return [feed_item for feed_item in self.store.values() if feed_item.feed_id == feed.feed_id]

    def upsert_many(self, feed_items: List[FeedItem]) -> List[FeedItem]:
        for feed_item in feed_items:
            self.store[feed_item.feed_item_id] = feed_item
        return feed_items


class NewsItemRepository:
    def __init__(self):
        self.store: Dict[str, NewsItem] = {}

    def reset(self):
        self.store = {}

    def count(self) -> int:
        return len(self.store)

    def fetch_all_non_read_for_feed(self, feed: Feed, user: User) -> List[NewsItem]:
        return [
            news_item
            for news_item in self.store.values()
            if not news_item.is_read and news_item.feed_id == feed.feed_id and news_item.user_id == user.user_id
        ]

    def upsert_many(self, news_items: List[NewsItem]) -> List[NewsItem]:
        for news_item in news_items:
            self.store[news_item.news_item_id] = news_item
        return news_items

    def delete_user_feed(self, user: User, feed: Feed) -> int:
        keys = [
            news_item.news_item_id
            for news_item in self.store.values()
            if news_item.user_id == user.user_id and news_item.feed_id == feed.feed_id
        ]
        for key in keys:
            del self.store[key]
        return len(keys)

    def fetch_items(self, user: User, cursor: Optional[bytes], limit: Optional[int] = 15) -> Tuple[str, List[NewsItem]]:
        return "token", [
            news_item
            for news_item in self.store.values()
            if news_item.user_id == user.user_id and not news_item.is_read
        ]

    def fetch_read_items(
        self, user: User, cursor: Optional[bytes], limit: Optional[int] = 15
    ) -> Tuple[str, List[NewsItem]]:
        return "token", [
            news_item for news_item in self.store.values() if news_item.user_id == user.user_id and news_item.is_read
        ]

    def mark_items_as_read(self, user: User, news_item_ids: List[str]) -> None:
        for key in news_item_ids:
            if self.store[key].user_id == user.user_id:
                self.store[key].is_read = True


class UserRepository:
    def __init__(self):
        self.store: Dict[str, User] = {}

    def reset(self):
        self.store = {}

    def count(self) -> int:
        return len(self.store)

    def fetch_user_by_email(self, email_address: str) -> Optional[User]:
        users = [user for user in self.store.values() if user.email_address == email_address]
        if len(users) != 1:
            return None
        return users[0]

    def upsert(self, user_profile: User) -> User:
        self.store[user_profile.user_id] = user_profile
        return user_profile

    def upsert_many(self, users: List[User]) -> List[User]:
        for user in users:
            self.upsert(user)
        return users

    def fetch_subscribed_to(self, feed: Feed) -> List[User]:
        return [user for user in self.store.values() if feed.feed_id in user.subscribed_to]


class MockRepositories:
    def __init__(self):
        log.warning("Initializing MOCK repositories")
        self.client = MagicMock(Client)
        self.user_repository = UserRepository()
        self.news_item_repository = NewsItemRepository()
        self.feed_item_repository = FeedItemRepository()
        self.feed_repository = FeedRepository()
        self.subscription_repository = SubscriptionRepository()
        self.client_session = MagicMock(ClientSession)  # type: ignore

    def mock_client_session_for_files(self, file_names: List[str]) -> ClientSession:
        def _response_for_file(file_name: str) -> AsyncMock:
            with open(file_name) as file:
                read_in_file = file.read()
                text_response = AsyncMock(ClientResponse)
                text_response.text.return_value = read_in_file
                text_response.read.return_value = bytes(read_in_file, "utf-8")

                response = Mock()
                response.__aenter__ = AsyncMock(return_value=text_response)
                response.__aexit__ = AsyncMock(return_value=None)
                return response

        client_session = AsyncMock(ClientSession)
        client_session.get.side_effect = [_response_for_file(file_name) for file_name in file_names]
        self.client_session = client_session
        return client_session

    def reset(self):
        self.user_repository.reset()
        self.news_item_repository.reset()
        self.feed_repository.reset()
        self.feed_item_repository.reset()
        self.subscription_repository.reset()

        self.client.reset_mock()
        self.client_session.reset_mock()
        feed_gemeente_groningen.number_of_items = 0
        feed_gemeente_groningen.number_of_subscriptions = 0
