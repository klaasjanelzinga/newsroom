import asyncio
from os import getenv
from typing import List
from unittest.mock import Mock, MagicMock, AsyncMock

import pytest
from aiohttp import ClientSession, ClientResponse
from faker import Faker
from motor.motor_asyncio import AsyncIOMotorClient
from starlette.responses import Response

import core_lib.app_config
from api import api_application_data
from api.security import TokenVerifier, Security
from core_lib import application_data
from core_lib.application_data import Repositories
from core_lib.feed_utils import upsert_gemeente_groningen_feed

core_lib.app_config.AppConfig.token_secret_key = Mock(return_value="junit-test-token")

from api.feed_api import fetch_feed_information_for_url, subscribe_to_feed
from core_lib.repositories import (
    User,
    Feed,
    FeedItem,
)
from core_lib.user import _generate_salt, _generate_hash
from core_lib.utils import bytes_to_str_base64


class ClientSessionMocker:
    def __init__(self, repositories: Repositories):
        self.repositories = repositories

    def setup_client_session_for(self, file_names: List[str]) -> None:
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
        self.repositories.client_session = client_session


def feed_factory(faker: Faker) -> Feed:
    return Feed(
        url=faker.url(),
        title=faker.sentence(),
        link=faker.url(),
        description=faker.sentence(),
        number_of_subscriptions=faker.pyint(),
        number_of_items=faker.pyint(),
    )


def feed_item_factory(faker: Faker, feed: Feed) -> FeedItem:
    return FeedItem(
        feed_id=feed.feed_id,
        title=faker.sentence(),
        link=faker.url(),
        description=faker.paragraph(),
        published=faker.date_time_between("-30d", "now"),
        created_on=faker.date_time_between("-20d", "now"),
        last_seen=faker.date_time_between("-4d", "now"),
    )


@pytest.fixture(scope="session")
def mongo_url() -> str:
    mongo_port = getenv("MONGO_PORT", "5011")
    mongo_host = getenv("MONGO_HOST", "localhost")
    return f"mongodb://newsroom_test:test@{mongo_host}:{mongo_port}/newsroom-test"


@pytest.fixture(scope="session")
def mongo_db() -> str:
    return "newsroom-test"


@pytest.fixture(scope="session")
def mongodb_client(mongo_url) -> AsyncIOMotorClient:
    return AsyncIOMotorClient(mongo_url)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def faker() -> Faker:
    return Faker()


@pytest.fixture
async def client_session():
    client_session = ClientSession()
    yield client_session
    await client_session.close()


async def clean_data_repositories(repository: Repositories) -> None:
    await repository.feed_repository.feeds_collection.delete_many({})
    await repository.feed_item_repository.feed_items_collection.delete_many({})
    await repository.news_item_repository.news_item_collection.delete_many({})
    await repository.saved_news_item_repository.saved_items_collection.delete_many({})


async def clean_repositories(repository: Repositories) -> None:
    await repository.user_repository.users_collection.delete_many({})
    await clean_data_repositories(repository)


@pytest.fixture()
async def repositories(mongodb_client: AsyncIOMotorClient, mongo_db: str, client_session: ClientSession) -> Repositories:
    repository = Repositories(client=mongodb_client, mongodb_db=mongo_db, client_session=client_session)
    application_data._repositories = repository
    api_application_data._security = Security(repository.user_repository)

    await clean_repositories(repository)
    return repository


@pytest.fixture()
def client_session_mocker(repositories: Repositories) -> ClientSessionMocker:
    return ClientSessionMocker(repositories)


@pytest.fixture
def user_password(faker: Faker) -> str:
    return faker.password(length=16, special_chars=True, digits=True, upper_case=True, lower_case=True)


@pytest.fixture
def user_password_salt() -> bytes:
    return _generate_salt()


@pytest.fixture
def user_password_hash(user_password: str, user_password_salt: bytes) -> bytes:
    return _generate_hash(user_password, user_password_salt)


@pytest.fixture
async def user(faker: Faker, repositories: Repositories, user_password_hash: bytes, user_password_salt: bytes) -> User:
    user = User(
        email_address=faker.email(),
        password_hash=bytes_to_str_base64(user_password_hash),
        password_salt=bytes_to_str_base64(user_password_salt),
        is_approved=True,
    )
    await repositories.user_repository.upsert(user)
    return user


@pytest.fixture
def user_bearer_token(faker: Faker, user: User) -> str:
    return f"Bearer {TokenVerifier.create_token(user)}"


@pytest.fixture
async def feed(faker: Faker, repositories: Repositories) -> Feed:
    feed = await repositories.feed_repository.upsert(feed_factory(faker))
    return feed


@pytest.fixture
async def feed_items(faker: Faker, repositories: Repositories, feed: Feed) -> List[FeedItem]:
    number_of_items = faker.pyint(min_value=10, max_value=20)
    feed_items = [feed_item_factory(faker, feed) for i in range(0, number_of_items)]
    return await repositories.feed_item_repository.upsert_many(feed_items)


@pytest.fixture
async def subscription(repositories: Repositories, user: User, feed: Feed) -> Feed:  # TODO rename to subscribed_feed or
    user.subscribed_to.append(feed.feed_id)
    feed.number_of_items += 1
    await repositories.feed_repository.upsert(feed)
    await repositories.user_repository.upsert(user)
    return feed


@pytest.fixture
async def user_with_subscription_to_feed(
    repositories: Repositories,
    client_session_mocker: ClientSessionMocker,
    faker: Faker,
    user: User,
    user_bearer_token: str,
) -> User:
    test_url = faker.url()

    # Find the unknown feed. Should fetch 1 feed item.
    client_session_mocker.setup_client_session_for(["sample-files/rss_feeds/pitchfork_best.xml"])
    response = MagicMock(Response)
    feed_response = await fetch_feed_information_for_url(response, test_url, authorization=user_bearer_token)
    feed = feed_response.feed
    assert await repositories.feed_item_repository.count({}) == 25
    assert feed_response is not None

    # subscribe the user, there should be 25 news-items
    await subscribe_to_feed(feed.feed_id.__str__(), authorization=user_bearer_token)
    assert await repositories.news_item_repository.count({}) == 25

    return user


@pytest.fixture
async def feed_gemeente_groningen(repositories: Repositories) -> Feed:
    return await upsert_gemeente_groningen_feed()
