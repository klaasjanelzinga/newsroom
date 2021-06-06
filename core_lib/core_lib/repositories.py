from dataclasses import dataclass
from datetime import datetime
import enum
from typing import Any, Dict, Iterator, List, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
import pydantic
from pydantic import Field
from pydantic.main import BaseModel
from pymongo import ASCENDING, DESCENDING, ReplaceOne
import pytz

from core_lib.utils import now_in_utc


def uuid4_str() -> ObjectId:
    return ObjectId()


@dataclass
class QueryResult:
    items: Iterator
    token: bytes


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls) -> ObjectId:
        yield cls.validate

    @classmethod
    def validate(cls, value: Any) -> ObjectId:
        if not ObjectId.is_valid(value):
            raise ValueError("Invalid objectid")
        return ObjectId(value)

    @classmethod
    def __modify_schema__(cls, field_schema: Any) -> None:
        field_schema.update(type="string")


class Avatar(BaseModel):
    user_id: PyObjectId = Field(default_factory=uuid4_str, alias="_id")
    image: str


class User(BaseModel):  # pylint: disable=too-few-public-methods
    user_id: PyObjectId = Field(default_factory=uuid4_str, alias="_id")
    email_address: str
    display_name: Optional[str]
    password_hash: str
    password_salt: str
    otp_hash: Optional[str]
    otp_backup_codes: List[str] = Field(default_factory=list)
    pending_otp_hash: Optional[str]
    pending_backup_codes: List[str] = Field(default_factory=list)
    is_approved: bool
    subscribed_to: List[PyObjectId] = []
    number_of_unread_items: int = 0


class FeedSourceType(str, enum.Enum):
    ATOM = "ATOM FEED"
    RSS = "RSS FEED"
    GEMEENTE_GRONINGEN = "GEMEENTE GRONINGEN FEED"
    RDF = "RDF FEED"


class Feed(BaseModel):  # pylint: disable=too-few-public-methods
    feed_id: PyObjectId = Field(default_factory=uuid4_str, alias="_id")
    url: str
    title: str
    link: str
    feed_source_type: FeedSourceType = FeedSourceType.RSS
    number_of_subscriptions: int = 0
    number_of_items: int = 0

    description: Optional[str]
    category: Optional[str]
    image_url: Optional[str]
    image_title: Optional[str]
    image_link: Optional[str]

    last_fetched: Optional[datetime]
    last_published: Optional[datetime]


class FeedItem(BaseModel):  # pylint: disable=too-few-public-methods
    feed_item_id: PyObjectId = Field(default_factory=uuid4_str, alias="_id")
    feed_id: PyObjectId

    title: str
    link: str
    description: Optional[str]
    last_seen: datetime
    published: Optional[datetime]
    created_on: datetime


class NewsItem(BaseModel):  # pylint: disable=too-few-public-methods
    news_item_id: PyObjectId = Field(default_factory=uuid4_str, alias="_id")
    feed_id: PyObjectId
    user_id: PyObjectId
    feed_item_id: PyObjectId

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
    is_read_on: Optional[datetime] = None
    saved_news_item_id: Optional[PyObjectId] = None

    def append_alternate(self, link: str, title: str, icon_link: str) -> None:
        """Append an alternate source for the news. Only appended if not yet present."""
        if link not in self.alternate_links:
            self.title = f"[Updated] {self.title}" if not self.title.startswith("[Updated] ") else self.title
            self.alternate_title_links.append(title)
            self.alternate_links.append(link)
            self.alternate_favicons.append(icon_link)


class SavedNewsItem(BaseModel):
    saved_news_item_id: PyObjectId = Field(default_factory=uuid4_str, alias="_id")

    feed_id: PyObjectId
    user_id: PyObjectId
    feed_item_id: PyObjectId
    news_item_id: PyObjectId

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
    def __init__(self, database: AsyncIOMotorDatabase):
        self.saved_items_collection = database["saved_items"]

    async def count(self, search_filter: Dict[str, Any]) -> int:
        """Count the number of documents in the collection."""
        return await self.saved_items_collection.count_documents(search_filter)

    async def fetch_items(self, user: User, offset: int, limit: int) -> List[SavedNewsItem]:
        result = (
            self.saved_items_collection.find(
                {"user_id": user.user_id}, sort=[("saved_on", DESCENDING), ("_id", ASCENDING)]
            )
            .skip(offset)
            .limit(limit)
        )
        return [SavedNewsItem.parse_obj(item) async for item in result]

    async def upsert(self, saved_news_item: SavedNewsItem) -> SavedNewsItem:
        await self.saved_items_collection.replace_one(
            {"_id": saved_news_item.saved_news_item_id}, saved_news_item.dict(by_alias=True), True
        )
        return saved_news_item

    async def delete_saved_news_item(self, saved_news_item_id: str, user: User) -> None:
        await self.saved_items_collection.delete_one({"_id": ObjectId(saved_news_item_id), "user_id": user.user_id})

    async def fetch_by_id(self, saved_news_item_id: str) -> Optional[SavedNewsItem]:
        result = await self.saved_items_collection.find_one({"_id": ObjectId(saved_news_item_id)})
        if result is None:
            return None
        return SavedNewsItem.parse_obj(result)


class FeedRepository:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.feeds_collection = database.get_collection("feeds")

    async def count(self, search_filter: Dict[str, Any]) -> int:
        """Count the number of documents in the collection."""
        return await self.feeds_collection.count_documents(search_filter)

    async def find_by_url(self, url: str) -> Optional[Feed]:
        """Check if a feed already exists by looking at the URL."""
        result = await self.feeds_collection.find_one({"url": url})
        if result is None:
            return None
        return Feed.parse_obj(result)

    async def upsert(self, feed: Feed) -> Feed:
        """Upsert a feed into the repository."""
        await self.feeds_collection.replace_one({"_id": feed.feed_id}, feed.dict(by_alias=True), True)
        return feed

    async def upsert_many(self, feeds: List[Feed]) -> List[Feed]:
        """Upsert feeds."""
        if len(feeds) > 0:
            requests = [ReplaceOne({"_id": feed.feed_id}, feed.dict(by_alias=True), True) for feed in feeds]
            await self.feeds_collection.bulk_write(requests)
        return feeds

    async def all_feeds(self) -> List[Feed]:
        """Retrieve all the feeds in the system."""
        result = self.feeds_collection.find({})
        return [Feed.parse_obj(feed) async for feed in result]

    async def get(self, feed_id: str) -> Feed:
        result = await self.feeds_collection.find_one({"_id": ObjectId(feed_id)})
        if result is None:
            raise Exception(f"Feed with id {feed_id} not found.")
        return Feed.parse_obj(result)

    async def get_active_feeds(self) -> List[Feed]:
        """Find the Feed entities that are actively used."""
        result = self.feeds_collection.find({"number_of_subscriptions": {"$gt": 0}})
        return [Feed.parse_obj(feed) async for feed in result]


class FeedItemRepository:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.feed_items_collection = database["feed_items"]

    async def count(self, search_filter: Dict[str, Any]) -> int:
        """Count the number of documents in the collection."""
        return await self.feed_items_collection.count_documents(search_filter)

    async def fetch_all_for_feed(self, feed: Feed) -> List[FeedItem]:
        result = self.feed_items_collection.find({"feed_id": feed.feed_id})
        return [FeedItem.parse_obj(feed_item) async for feed_item in result]

    async def count_all_for_feed(self, feed: Feed) -> int:
        return await self.feed_items_collection.count_documents({"feed_id": feed.feed_id})

    async def upsert_many(self, feed_items: List[FeedItem]) -> List[FeedItem]:
        """Upsert feed items."""
        if len(feed_items) > 0:
            requests = [
                ReplaceOne({"_id": feed_item.feed_item_id}, feed_item.dict(by_alias=True), True)
                for feed_item in feed_items
            ]
            await self.feed_items_collection.bulk_write(requests)
        return feed_items

    async def delete_older_than(self, before: datetime) -> int:
        response = await self.feed_items_collection.delete_many({"last_seen": {"$lt": before}})
        return response.deleted_count


class NewsItemRepository:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database
        self.news_item_collection = database["news_items"]

    async def count(self, search_filter: Dict[str, Any]) -> int:
        """Count the number of documents in the collection."""
        return await self.news_item_collection.count_documents(search_filter)

    async def upsert_many(self, news_items: List[NewsItem]) -> List[NewsItem]:
        if len(news_items) > 0:
            replace_requests = [
                ReplaceOne({"_id": news_item.news_item_id}, news_item.dict(by_alias=True), True)
                for news_item in news_items
            ]
            await self.news_item_collection.bulk_write(replace_requests)
        return news_items

    async def upsert(self, news_item: NewsItem) -> NewsItem:
        await self.news_item_collection.replace_one(
            {"_id": news_item.news_item_id}, news_item.dict(by_alias=True), True
        )
        return news_item

    async def delete_user_feed(self, user: User, feed: Feed) -> int:
        result = await self.news_item_collection.delete_many({"user_id": user.user_id, "feed_id": feed.feed_id})
        return result.deleted_count

    async def fetch_items(self, user: User, limit: int) -> List[NewsItem]:
        result = self.news_item_collection.find(
            {"user_id": user.user_id, "is_read": False}, sort=[("published", DESCENDING)]
        ).limit(limit)

        return [NewsItem.parse_obj(item) async for item in result]

    async def fetch_read_items(self, user: User, offset: int, limit: int) -> List[NewsItem]:
        result = (
            self.news_item_collection.find(
                {"user_id": user.user_id, "is_read": True}, sort=[("published", ASCENDING), ("_id", ASCENDING)]
            )
            .skip(offset)
            .limit(limit)
        )
        return [NewsItem.parse_obj(item) async for item in result]

    async def fetch_by_id(self, news_item_id: str) -> Optional[NewsItem]:
        result = await self.news_item_collection.find_one({"_id": ObjectId(news_item_id)})
        if result is None:
            return None
        return NewsItem.parse_obj(result)

    async def fetch_all_non_read_for_feed(self, feed: Feed, user: User) -> List[NewsItem]:
        result = self.news_item_collection.find({"feed_id": feed.feed_id, "is_read": False, "user_id": user.user_id})
        return [NewsItem.parse_obj(item) async for item in result]

    async def mark_items_as_read(self, user: User, news_item_ids: List[str]) -> None:
        await self.news_item_collection.update_many(
            {"_id": {"$in": [PyObjectId(news_item_id) for news_item_id in news_item_ids]}, "user_id": user.user_id},
            {"$set": {"is_read": True, "is_read_on": datetime.now(tz=pytz.utc)}},
        )

    async def delete_read_items_older_than(self, before: datetime) -> int:
        result = await self.news_item_collection.delete_many({"is_read": True, "is_read_on": {"$lt": before}})
        return result.deleted_count


class UserRepository:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.users_collection = database["users"]
        self.avatars = database["avatars"]
        self.feeds = database["feeds"]

    async def count(self, search_filter: Dict[str, Any]) -> int:
        """Count the number of documents in the collection."""
        return await self.users_collection.count_documents(search_filter)

    async def fetch_user_by_email(self, email_address: str) -> Optional[User]:
        result = await self.users_collection.find_one({"email_address": email_address})
        if result is None:
            return None
        return User.parse_obj(result)

    async def upsert(self, user: User) -> User:
        await self.users_collection.replace_one({"_id": user.user_id}, user.dict(by_alias=True), True)
        return user

    async def upsert_many(self, users: List[User]) -> List[User]:
        if len(users) > 0:
            replace_requests = [ReplaceOne({"_id": user.user_id}, user.dict(by_alias=True), True) for user in users]
            await self.users_collection.bulk_write(replace_requests)
        return users

    async def fetch_subscribed_to(self, feed: Feed) -> List[User]:
        result = self.users_collection.find()
        users = [User.parse_obj(user) async for user in result]
        return [user for user in users if feed.feed_id in user.subscribed_to]

    async def update_avatar(self, user: User, avatar_image: Optional[str]) -> Optional[Avatar]:
        if avatar_image is None:
            self.avatars.delete_many({"_id": user.user_id})
            return None
        avatar = Avatar(image=avatar_image)
        avatar.user_id = user.user_id
        await self.avatars.replace_one({"_id": user.user_id}, avatar.dict(by_alias=True), True)
        return avatar

    async def fetch_avatar_for_user(self, user: User) -> Optional[Avatar]:
        avatar = await self.avatars.find_one({"_id": user.user_id})
        if avatar is None:
            return None
        return Avatar.parse_obj(avatar)


class RefreshResult(pydantic.main.BaseModel):
    feed: Feed
    number_of_items: int
