from contextlib import contextmanager
from typing import Tuple
from unittest.mock import Mock, AsyncMock

import pytest
from faker import Faker

from core_lib import application_data
from core_lib.repositories import (
    User,
    Feed,
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
    return Feed(
        url=faker.url(),
        title=faker.sentence(),
        link=faker.url(),
        description=faker.sentence(),
        number_of_subscriptions=faker.pyint(),
        number_of_items=faker.pyint(),
    )


@pytest.fixture
def repositories():
    repositories = application_data.repositories
    repositories.reset_mocks()
    repositories.mock_subscription_repository().upsert.side_effect = mirror_side_effect
    repositories.mock_user_repository().upsert.side_effect = mirror_side_effect
    repositories.mock_feed_repository().upsert.side_effect = mirror_side_effect
    return application_data.repositories


def mirror_side_effect(arg):
    return arg


@pytest.fixture
def subscribed_user(user: User, feed: Feed) -> Tuple[User, Feed]:
    user.subscribed_to = [feed.feed_id]
    feed.number_of_subscriptions = 1
    return user, feed


@contextmanager
def authorization_for(security_mock: Mock, user: User):
    security_mock.get_approved_user = AsyncMock()
    security_mock.get_approved_user.return_value = user

    yield

    security_mock.get_approved_user.assert_called_once()
