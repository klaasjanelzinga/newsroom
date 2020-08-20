from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional

from google.cloud import datastore
from google.cloud.client import Client
from pydantic import BaseModel


class User(BaseModel):
    class Config:
        allow_mutation = False
    email: str
    given_name: str
    family_name: str
    avatar_url: str
    is_approved: bool


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


@dataclass
class Feed:
    url: str
    description: str
    last_fetched: datetime


@dataclass
class FeedItem:
    id: str
    body: str
    url: str
    feed: Feed


@dataclass
class Subscription:
    feed_id: str
    user_id: str
    tags: List[str]


@dataclass
class NewsItem:
    feed_item: FeedItem
    user_id: str
    is_read: bool
    is_saved: bool
    tags: List[str]
