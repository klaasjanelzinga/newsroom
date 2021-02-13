from typing import List

import pytest
from faker import Faker

from api.security import TokenVerifier
from core_lib import application_data
from core_lib.application_data import Repositories, repositories
from core_lib.repositories import (
    User,
    Feed,
    FeedItem,
    Subscription,
)
from core_lib.user import _generate_salt, _generate_hash
from core_lib.utils import bytes_to_str_base64
from tests.mock_repositories import MockRepositories

application_data.repositories = MockRepositories()
application_data.token_secret_key = "junit-secret"

if application_data.repositories is None:
    print("Oeps")


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


@pytest.fixture
def faker() -> Faker:
    return Faker()


@pytest.fixture
def repositories() -> Repositories:
    repositories = application_data.repositories
    repositories.reset()
    return application_data.repositories


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
def user(faker: Faker, repositories: MockRepositories, user_password_hash: bytes, user_password_salt: bytes) -> User:
    user = User(
        email_address=faker.email(),
        password_hash=bytes_to_str_base64(user_password_hash),
        password_salt=bytes_to_str_base64(user_password_salt),
        is_approved=True,
    )
    repositories.user_repository.upsert(user)
    return user


@pytest.fixture
def user_bearer_token(faker: Faker, user: User) -> str:
    return f"Bearer {TokenVerifier.create_token(user)}"


@pytest.fixture
def feed(faker: Faker, repositories: Repositories) -> Feed:
    feed = repositories.feed_repository.upsert(feed_factory(faker))
    return feed


@pytest.fixture
def feed_items(faker: Faker, repositories: Repositories, feed: Feed) -> List[FeedItem]:
    number_of_items = faker.pyint(min_value=10, max_value=20)
    feed_items = [feed_item_factory(faker, feed) for i in range(0, number_of_items)]
    return repositories.feed_item_repository.upsert_many(feed_items)


@pytest.fixture
def subscription(repositories: Repositories, user: User, feed: Feed) -> Subscription:
    user.subscribed_to.append(feed.feed_id)
    feed.number_of_items += 1
    repositories.feed_repository.upsert(feed)
    repositories.user_repository.upsert(user)
    return repositories.subscription_repository.upsert(Subscription(user_id=user.user_id, feed_id=feed.feed_id))
