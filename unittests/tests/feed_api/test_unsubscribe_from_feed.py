from typing import Tuple, List
from unittest.mock import patch, Mock

import pytest
from faker import Faker

from api.feed_api import unsubscribe_from_feed
from core_lib.feed import subscribe_user_to_feed
from core_lib.feed_utils import news_items_from_feed_items, news_item_from_feed_item
from core_lib.repositories import User, Feed, FeedItem, Subscription
from tests.conftest import authorization_for
from tests.mock_repositories import MockRepositories


@pytest.mark.asyncio
@patch("api.feed_api.security")
async def test_unsubscribe(
    security_mock: Mock,
    user: User,
    feed: Feed,
    feed_items: List[FeedItem],
    repositories: MockRepositories,
):
    number_of_subscriptions = feed.number_of_subscriptions
    assert user.number_of_unread_items == 0
    subscribe_user_to_feed(user, feed)
    assert feed.number_of_subscriptions == 1 + number_of_subscriptions
    assert user.number_of_unread_items == len(feed_items)
    assert feed.feed_id in user.subscribed_to

    with authorization_for(security_mock, user, repositories):
        response = await unsubscribe_from_feed(feed_id=feed.feed_id, authorization="patched")
        assert feed.feed_id not in response.subscribed_to
        assert feed.number_of_subscriptions == number_of_subscriptions
        assert user.number_of_unread_items == 0

        # All items for the user are deleted.
        assert repositories.news_item_repository.count() == 0
        assert repositories.subscription_repository.count() == 0


@pytest.mark.asyncio
@patch("api.feed_api.security")
async def test_unscubscribe_while_already_unscubscribed(
    security_mock: Mock, faker: Faker, user: User, feed: Feed, repositories: MockRepositories
):
    number_of_subscriptions = feed.number_of_subscriptions
    assert feed.feed_id not in user.subscribed_to

    with authorization_for(security_mock, user, repositories):
        response = await unsubscribe_from_feed(feed_id=feed.feed_id, authorization=faker.word())
        assert feed.feed_id not in response.subscribed_to
        assert feed.number_of_subscriptions == number_of_subscriptions
