import base64
from dataclasses import dataclass
from datetime import datetime
import enum
from typing import Any, Iterator, List, Optional, Tuple
from uuid import uuid4

from google.cloud import datastore
from google.cloud.datastore import Client, Key, Query
import pydantic
from pydantic import Field
from pydantic.main import BaseModel

from core_lib.utils import now_in_utc


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


class Avatar(BaseModel):
    user_id: str
    image: str


class User(BaseModel):  # pylint: disable=too-few-public-methods
    user_id: str = Field(default_factory=uuid4_str)
    email_address: str
    display_name: Optional[str]
    password_hash: str
    password_salt: str
    otp_hash: Optional[str]
    otp_backup_codes: List[str] = Field(default_factory=list)
    pending_otp_hash: Optional[str]
    pending_backup_codes: List[str] = Field(default_factory=list)
    is_approved: bool
    subscribed_to: List[str] = []
    number_of_unread_items: int = 0


class FeedSourceType(enum.Enum):
    ATOM = 0
    RSS = 1
    HTML = 2
    RDF = 3


class Feed(BaseModel):  # pylint: disable=too-few-public-methods
    feed_id: str = Field(default_factory=uuid4_str)
    url: str
    title: str
    link: str
    feed_source_type: str = FeedSourceType.RSS.name
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
    alternate_links: List[str] = Field(default_factory=list)
    alternate_title_links: List[str] = Field(default_factory=list)
    alternate_favicons: List[str] = Field(default_factory=list)
    favicon: Optional[str]

    created_on: datetime = now_in_utc()
    is_read: bool = False
    is_saved: bool = False
    saved_news_item_id: Optional[str] = None

    def append_alternate(self, link: str, title: str, icon_link: str) -> None:
        """ Append an alternate source for the news. Only appended if not yet present. """
        if link not in self.alternate_links:
            self.title = f"[Updated] {self.title}" if not self.title.startswith("[Updated] ") else self.title
            self.alternate_title_links.append(title)
            self.alternate_links.append(link)
            self.alternate_favicons.append(icon_link)


class SavedNewsItem(BaseModel):
    saved_news_item_id: str = Field(default_factory=uuid4_str)

    feed_id: str
    user_id: str
    feed_item_id: str
    news_item_id: str

    feed_title: str
    title: str
    description: str
    link: str
    published: datetime
    alternate_links: List[str] = Field(default_factory=list)
    alternate_title_links: List[str] = Field(default_factory=list)
    alternate_favicons: List[str] = Field(default_factory=list)
    favicon: Optional[str]

    created_on: datetime
    saved_on: datetime = now_in_utc()


class SavedNewsItemRepository:
    def __init__(self, client: Client):
        self.client = client

    def fetch_items(
        self, user: User, cursor: Optional[bytes], limit: Optional[int] = 15
    ) -> Tuple[str, List[SavedNewsItem]]:
        google_cursor = create_cursor(earlier_cursor=cursor)
        if google_cursor is not None and google_cursor.decode("utf-8") == "DONE":
            return base64.encodebytes(b"DONE").decode("utf-8"), []
        query = self.client.query(kind="SavedNewsItem")
        query.add_filter("user_id", "=", user.user_id)
        query.order = ["-saved_on"]

        token, entities = token_and_entities_for_query(cursor=google_cursor, query=query, limit=limit)
        return token, [SavedNewsItem.parse_obj(entity) for entity in entities]

    def upsert(self, saved_news_item: SavedNewsItem) -> SavedNewsItem:
        entity = datastore.Entity(self.client.key("SavedNewsItem", saved_news_item.saved_news_item_id))
        entity.update(saved_news_item.dict())
        self.client.put(entity)
        return SavedNewsItem.parse_obj(entity)

    def delete_saved_news_item(self, saved_news_item_id: str, user: User) -> None:
        key = self.client.key("SavedNewsItem", saved_news_item_id)
        data = self.client.get(key)
        if data["user_id"] == user.user_id:
            self.client.delete(data)

    def fetch_by_id(self, saved_news_item_id: str) -> Optional[SavedNewsItem]:
        key = self.client.key("SavedNewsItem", saved_news_item_id)
        data = self.client.get(key)
        if data is None:
            return None
        return SavedNewsItem.parse_obj(data)


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

    def count_all_for_feed(self, feed: Feed) -> int:
        query = self.client.query(kind="FeedItem")
        query.add_filter("feed_id", "=", feed.feed_id)
        return sum(1 for _ in query.fetch())

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

    def upsert(self, news_item: NewsItem) -> NewsItem:
        entity = datastore.Entity(self.client.key("NewsItem", news_item.news_item_id))
        entity.update(news_item.dict())
        self.client.put(entity)
        return NewsItem.parse_obj(entity)

    def delete_user_feed(self, user: User, feed: Feed) -> int:
        query = self.client.query(kind="NewsItem")
        query.add_filter("user_id", "=", user.user_id)
        query.add_filter("feed_id", "=", feed.feed_id)
        query.keys_only()
        entities = [entity.key for entity in query.fetch()]
        self.client.delete_multi(entities)
        return len(entities)

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

    def fetch_by_id(self, news_item_id: str) -> Optional[NewsItem]:
        key = self.client.key("NewsItem", news_item_id)
        data = self.client.get(key)
        if data is None:
            return None
        return NewsItem.parse_obj(data)

    def fetch_all_non_read_for_feed(self, feed: Feed, user: User) -> List[NewsItem]:
        query = self.client.query(kind="NewsItem")
        query.add_filter("feed_id", "=", feed.feed_id)
        query.add_filter("is_read", "=", False)
        query.add_filter("user_id", "=", user.user_id)
        return [NewsItem.parse_obj(news_item) for news_item in query.fetch()]

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

    def fetch_user_by_email(self, email_address: str) -> Optional[User]:
        query = self.client.query(kind="User")
        query.add_filter("email_address", "=", email_address)
        result = list(query.fetch())
        if not result:
            return None
        return User.parse_obj(result[0])

    def upsert(self, user: User) -> User:
        entity = datastore.Entity(self.client.key("User", user.user_id))
        entity.update(user.dict())
        self.client.put(entity)
        return User.parse_obj(entity)

    def upsert_many(self, users: List[User]) -> List[User]:
        entities = []
        for user in users:
            entity = datastore.Entity(self.client.key("User", user.user_id))
            entity.update(user.dict())
            entities.append(entity)

        self.client.put_multi(entities)
        return [User.parse_obj(entity) for entity in entities]

    def fetch_subscribed_to(self, feed: Feed) -> List[User]:
        query = self.client.query(kind="User")
        result = list(query.fetch())
        if not result:
            return []
        return [User.parse_obj(entity) for entity in result if feed.feed_id in entity["subscribed_to"]]

    def update_avatar(self, user: User, avatar_image: Optional[str]) -> Optional[Avatar]:
        entity = datastore.Entity(self.client.key("Avatar", user.user_id), exclude_from_indexes=["image"])
        if avatar_image is None:
            self.client.delete(entity)
            return None
        avatar = Avatar(user_id=user.user_id, image=avatar_image)
        entity.update(avatar.dict())
        self.client.put(entity)
        return Avatar.parse_obj(entity)

    def fetch_avatar_for_user(self, user: User) -> Optional[Avatar]:
        key = self.client.key("Avatar", user.user_id)
        data = self.client.get(key)
        if data is None:
            return None
        return Avatar.parse_obj(data)


class RefreshResult(pydantic.main.BaseModel):
    feed: Feed
    number_of_items: int
