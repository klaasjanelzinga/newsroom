from typing import Tuple

import pytest
from faker import Faker
from google.cloud.datastore import Client

from core_lib import application_data
from core_lib.repositories import (
    User,
    Feed,
    NewsItemRepository,
    SubscriptionRepository,
    FeedRepository,
    FeedItemRepository,
)


def mirror_side_effect(arg):
    return arg


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
def subscribed_user(user: User, feed: Feed) -> Tuple[User, Feed]:
    user.subscribed_to = [feed.feed_id]
    feed.number_of_subscriptions = 1
    return user, feed


@pytest.fixture
def mocked_datastore() -> Client:
    application_data.DATASTORE_CLIENT.reset_mock()
    return application_data.DATASTORE_CLIENT


@pytest.fixture
def news_item_repository() -> NewsItemRepository:
    application_data.news_item_repository.reset_mock()
    return application_data.news_item_repository


@pytest.fixture
def subscription_repository() -> SubscriptionRepository:
    application_data.subscription_repository.reset_mock()
    application_data.subscription_repository.upsert.side_effect = mirror_side_effect
    return application_data.subscription_repository


@pytest.fixture
def feed_repository() -> FeedRepository:
    application_data.feed_repository.reset_mock()
    application_data.feed_repository.upsert.side_effect = mirror_side_effect
    return application_data.feed_repository


@pytest.fixture
def feed_item_repository() -> FeedItemRepository:
    application_data.feed_item_repository.reset_mock()
    application_data.feed_item_repository.upsert_many.side_effect = mirror_side_effect
    return application_data.feed_item_repository
