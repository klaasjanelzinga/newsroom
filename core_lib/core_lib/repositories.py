from datetime import datetime
from typing import Optional, List
from uuid import uuid4

from google.cloud import datastore
from google.cloud.datastore import Client
from pydantic.main import BaseModel
from pydantic import Field


def uuid4_str() -> str:
    return uuid4().__str__()


class User(BaseModel):
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
    description: str
    number_of_subscriptions: int = 0
    number_of_items: int = 0

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
    description: str
    published: Optional[datetime]
    created_on: datetime


class NewsItem(BaseModel):  # pylint: disable=too-few-public-methods
    news_item_id: str = Field(default_factory=uuid4_str)
    feed_id: str
    user_id: str
    feed_item_id: str

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
        query.add_filter("user_id", "=", user.email)
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
        query.add_filter("user_id", "=", user.email)
        query.add_filter("feed_id", "=", feed.feed_id)
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
