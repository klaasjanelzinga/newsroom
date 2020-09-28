from contextlib import contextmanager
from typing import Tuple, List
from unittest.mock import Mock, AsyncMock

import pytest
from faker import Faker

from core_lib import application_data
from core_lib.repositories import (
    User,
    Feed,
    FeedItem,
    Subscription,
)
from tests.mock_repositories import MockRepositories

application_data.repositories = MockRepositories()


def feed_factory(faker: Faker) -> Feed:
    return Feed(
        url=faker.url(),
        title=faker.sentence(),
        link=faker.url(),
        description=faker.sentence(),
        number_of_subscriptions=faker.pyint(),
        number_of_items=faker.pyint(),
    )


@pytest.fixture
def faker() -> Faker:
    return Faker()


@pytest.fixture
def user(faker: Faker) -> User:
    user = User(
        given_name=faker.name(),
        family_name=faker.name(),
        email=faker.email(),
        avatar_url=faker.url(),
        is_approved=faker.pybool(),
    )
    return user


@pytest.fixture
def feed(faker: Faker) -> Feed:
    return feed_factory(faker)


@pytest.fixture
def feed_items(faker: Faker, feed: Feed) -> List[FeedItem]:
    number_of_items = faker.pyint(min_value=10, max_value=20)
    return [
        FeedItem(
            feed_id=feed.feed_id,
            title=faker.sentence(),
            link=faker.url(),
            description=faker.paragraph(),
            published=faker.date_time_between("-30d", "now"),
            created_on=faker.date_time_between("-20d", "now"),
            last_seen=faker.date_time_between("-4d", "now"),
        )
        for i in range(0, number_of_items)
    ]


@pytest.fixture
def subscription(user: User, feed: Feed) -> Subscription:
    return Subscription(user_id=user.user_id, feed_id=feed.feed_id)


@pytest.fixture
def repositories():
    repositories = application_data.repositories
    repositories.reset()
    return application_data.repositories


@pytest.fixture
def subscribed_user(user: User, feed: Feed) -> Tuple[User, Feed]:
    user.subscribed_to = [feed.feed_id]
    feed.number_of_subscriptions = 1
    return user, feed


@contextmanager
def authorization_for(security_mock: Mock, user: User, repositories: MockRepositories):
    security_mock.get_approved_user = AsyncMock()
    security_mock.get_approved_user.return_value = user
    repositories.user_repository.upsert(user)

    yield

    security_mock.get_approved_user.assert_called_once()
