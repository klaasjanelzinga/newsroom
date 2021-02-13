from typing import List

import pytest
from faker import Faker

from api.feed_api import unsubscribe_from_feed, subscribe_to_feed
from core_lib.repositories import User, Feed, FeedItem
from tests.mock_repositories import MockRepositories


@pytest.mark.asyncio
async def test_unsubscribe(
    user: User,
    feed: Feed,
    feed_items: List[FeedItem],
    repositories: MockRepositories,
    user_bearer_token,
):
    number_of_subscriptions = feed.number_of_subscriptions
    assert user.number_of_unread_items == 0
    await subscribe_to_feed(feed_id=feed.feed_id, authorization=user_bearer_token)
    assert feed.number_of_subscriptions == 1 + number_of_subscriptions
    assert user.number_of_unread_items == len(feed_items)
    assert feed.feed_id in user.subscribed_to

    response = await unsubscribe_from_feed(feed_id=feed.feed_id, authorization=user_bearer_token)
    assert feed.feed_id not in response.subscribed_to
    assert feed.number_of_subscriptions == number_of_subscriptions
    assert user.number_of_unread_items == 0

    # All items for the user are deleted.
    assert repositories.news_item_repository.count() == 0
    assert repositories.subscription_repository.count() == 0


@pytest.mark.asyncio
async def test_unscubscribe_while_already_unscubscribed(
    faker: Faker, user: User, feed: Feed, repositories: MockRepositories, user_bearer_token
):
    number_of_subscriptions = feed.number_of_subscriptions
    assert feed.feed_id not in user.subscribed_to

    response = await unsubscribe_from_feed(feed_id=feed.feed_id, authorization=user_bearer_token)
    assert feed.feed_id not in response.subscribed_to
    assert feed.number_of_subscriptions == number_of_subscriptions
