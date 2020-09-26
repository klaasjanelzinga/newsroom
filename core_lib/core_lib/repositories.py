import base64
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Iterator, Tuple, Any
from uuid import uuid4

from google.cloud import datastore
from google.cloud.datastore import Client, Query, Key
from pydantic.main import BaseModel
from pydantic import Field


def uuid4_str() -> str:
    return uuid4().__str__()


def create_cursor(earlier_cursor: Optional[bytes]) -> Optional[bytes]:
    return base64.decodebytes(earlier_cursor) if earlier_cursor is not None else None


def token_and_entities_for_query(query: Query, cursor: Optional[bytes], limit: Optional[int]) -> Tuple[str, Any]:
    query_iter = query.fetch(start_cursor=cursor, limit=limit)

    page = next(query_iter.pages)
    next_cursor = query_iter.next_page_token
    next_cursor_encoded = (
        base64.encodebytes(next_cursor) if next_cursor is not None else base64.encodebytes(bytes("DONE", "UTF-8"))
    )
    return next_cursor_encoded.decode("utf-8"), page


@dataclass
class QueryResult:
    items: Iterator
    token: bytes


class User(BaseModel):  # pylint: disable=too-few-public-methods
    user_id: str = Field(default_factory=uuid4_str)
    email: str
    given_name: str
    family_name: str
    avatar_url: str
    is_approved: bool
    subscribed_to: List[str] = []


class Feed(BaseModel):  # pylint: disable=too-few-public-methods
    feed_id: str = Field(default_factory=uuid4_str)
    url: str
    title: str
    link: str
    number_of_subscriptions: int = 0
    number_of_items: int = 0

    description: Optional[str]
    category: Optional[str]
    image_url: Optional[str]
    image_title: Optional[str]
    image_link: Optional[str]

    last_fetched: Optional[datetime]
    last_published: Optional[datetime]


class Subscription(BaseModel):  # pylint: disable=too-few-public-methods
    subscription_id: str = Field(default_factory=uuid4_str)
    feed_id: str
    user_id: str


class FeedItem(BaseModel):  # pylint: disable=too-few-public-methods
    feed_item_id: str = Field(default_factory=uuid4_str)
    feed_id: str

    title: str
    link: str
    description: Optional[str]
    last_seen: datetime
    published: Optional[datetime]
    created_on: datetime


class NewsItem(BaseModel):  # pylint: disable=too-few-public-methods
    news_item_id: str = Field(default_factory=uuid4_str)
    feed_id: str
    user_id: str
    feed_item_id: str

    feed_title: str
    title: str
    description: str
    link: str
    published: datetime

    is_read: bool = False


class FeedRepository:
    def __init__(self, client: Client):
        self.client = client

    def find_by_url(self, url: str) -> Optional[Feed]:
        """ Find the Feed entity for the url. """
        query = self.client.query(kind="Feed")
        query.add_filter("url", "=", url.rstrip("/"))
        result = list(query.fetch())
        if not result:
            return None
        return Feed.parse_obj(result[0])

    def upsert(self, feed: Feed) -> Feed:
        """ Upsert a feed into the repository. """
        entity = datastore.Entity(self.client.key("Feed", feed.feed_id))
        entity.update(feed.dict())
        self.client.put(entity)
        return Feed.parse_obj(entity)

    def all_feeds(self) -> List[Feed]:
        """ Retrieve all the feeds in the system. """
        query = self.client.query(kind="Feed")
        return [Feed.parse_obj(result) for result in query.fetch()]

    def get(self, feed_id: str) -> Feed:
        key = self.client.key("Feed", feed_id)
        data = self.client.get(key)
        if data is None:
            raise Exception(f"Feed with id {feed_id} not found.")
        return Feed.parse_obj(data)

    def get_active_feeds(self) -> List[Feed]:
        """ Find the Feed entities that are activily used. """
        query = self.client.query(kind="Feed")
        query.add_filter("number_of_subscriptions", ">", 0)
        result = list(query.fetch())
        if not result:
            return []
        return [Feed.parse_obj(entity) for entity in result]


class SubscriptionRepository:
    def __init__(self, client: Client):
        self.client = client

    def upsert(self, subscription: Subscription) -> Subscription:
        entity = datastore.Entity(self.client.key("Subscription", subscription.subscription_id))
        entity.update(subscription.dict())
        self.client.put(entity)
        return Subscription.parse_obj(entity)

    def delete_user_feed(self, user: User, feed: Feed) -> None:
        query = self.client.query(kind="Subscription")
        query.add_filter("user_id", "=", user.user_id)
        query.add_filter("feed_id", "=", feed.feed_id)
        query.keys_only()
        self.client.delete_multi([entity.key for entity in query.fetch()])


class FeedItemRepository:
    def __init__(self, client: Client):
        self.client = client

    def fetch_all_for_feed(self, feed: Feed) -> List[FeedItem]:
        query = self.client.query(kind="FeedItem")
        query.add_filter("feed_id", "=", feed.feed_id)
        return [FeedItem.parse_obj(feed_item) for feed_item in query.fetch()]

    def upsert_many(self, feed_items: List[FeedItem]) -> List[FeedItem]:
        entities = []
        for feed_item in feed_items:
            entity = datastore.Entity(self.client.key("FeedItem", feed_item.feed_item_id))
            entity.update(feed_item.dict())
            entities.append(entity)

        self.client.put_multi(entities)
        return [FeedItem.parse_obj(entity) for entity in entities]

    def fetch_all_last_seen_before(self, before: datetime) -> List[str]:
        query = self.client.query(kind="FeedItem")
        query.add_filter("last_seen", "<", before)
        query.keys_only()
        return [entity.key for entity in query.fetch()]

    def delete_keys(self, keys: List[Key]) -> None:
        self.client.delete_multi(keys)


class NewsItemRepository:
    def __init__(self, client: Client):
        self.client = client

    def upsert_many(self, news_items: List[NewsItem]) -> List[NewsItem]:
        entities = []
        for news_item in news_items:
            entity = datastore.Entity(self.client.key("NewsItem", news_item.news_item_id))
            entity.update(news_item.dict())
            entities.append(entity)

        self.client.put_multi(entities)
        return [NewsItem.parse_obj(entity) for entity in entities]

    def delete_user_feed(self, user: User, feed: Feed) -> None:
        query = self.client.query(kind="NewsItem")
        query.add_filter("user_id", "=", user.user_id)
        query.add_filter("feed_id", "=", feed.feed_id)
        query.keys_only()
        self.client.delete_multi([entity.key for entity in query.fetch()])

    def fetch_items(self, user: User, cursor: Optional[bytes], limit: Optional[int] = 15) -> Tuple[str, List[NewsItem]]:
        google_cursor = create_cursor(earlier_cursor=cursor)
        if google_cursor is not None and google_cursor.decode("utf-8") == "DONE":
            return base64.encodebytes(b"DONE").decode("utf-8"), []
        query = self.client.query(kind="NewsItem")
        query.add_filter("user_id", "=", user.user_id)
        query.add_filter("is_read", "=", False)
        query.order = ["-published"]

        token, entities = token_and_entities_for_query(cursor=google_cursor, query=query, limit=limit)
        return token, [NewsItem.parse_obj(entity) for entity in entities]

    def fetch_read_items(
        self, user: User, cursor: Optional[bytes], limit: Optional[int] = 15
    ) -> Tuple[str, List[NewsItem]]:
        google_cursor = create_cursor(earlier_cursor=cursor)
        if google_cursor is not None and google_cursor.decode("utf-8") == "DONE":
            return base64.encodebytes(b"DONE").decode("utf-8"), []
        query = self.client.query(kind="NewsItem")
        query.add_filter("user_id", "=", user.user_id)
        query.add_filter("is_read", "=", True)
        query.order = ["-published"]

        token, entities = token_and_entities_for_query(cursor=google_cursor, query=query, limit=limit)
        return token, [NewsItem.parse_obj(entity) for entity in entities]

    def mark_items_as_read(self, user: User, news_item_ids: List[str]) -> None:
        keys = [self.client.key("NewsItem", key) for key in news_item_ids]
        entities = self.client.get_multi(keys)
        for entity in entities:
            if entity["user_id"] == user.user_id:
                entity["is_read"] = True
        self.client.put_multi(entities)

    def filter_feed_item_keys_that_are_read(self, feed_item_keys: List[Key]) -> List[Key]:
        result = []
        for feed_item_key in feed_item_keys:
            query = self.client.query(kind="NewsItem")
            query.add_filter("feed_item_id", "=", feed_item_key.name)
            query.add_filter("is_read", "=", False)
            query.keys_only()
            number_hits = len(list(query.fetch()))
            if number_hits == 0:
                result.append(feed_item_key)
        return result

    def delete_with_feed_item_keys(self, feed_item_keys: List[Key]) -> None:
        for feed_item_id in feed_item_keys:
            query = self.client.query(kind="NewsItem")
            query.add_filter("feed_item_id", "=", feed_item_id.name)
            query.keys_only()
            self.client.delete_multi([entity.key for entity in query.fetch()])


class UserRepository:
    def __init__(self, client: Client):
        self.client = client

    def fetch_user_by_email(self, email: str) -> Optional[User]:
        query = self.client.query(kind="User")
        query.add_filter("email", "=", email)
        result = list(query.fetch())
        if not result:
            return None
        return User.parse_obj(result[0])

    def upsert(self, user_profile: User) -> User:
        entity = datastore.Entity(self.client.key("User", user_profile.email))
        entity.update(user_profile.dict())
        self.client.put(entity)
        return User.parse_obj(entity)

    def fetch_subscribed_to(self, feed: Feed) -> List[User]:
        query = self.client.query(kind="User")
        result = list(query.fetch())
        if not result:
            return []
        return [User.parse_obj(entity) for entity in result if feed.feed_id in entity["subscribed_to"]]
