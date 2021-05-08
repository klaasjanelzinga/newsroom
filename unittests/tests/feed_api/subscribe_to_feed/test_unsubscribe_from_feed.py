from typing import List

import pytest
from faker import Faker

from api.feed_api import unsubscribe_from_feed, subscribe_to_feed
from core_lib.application_data import Repositories
from core_lib.repositories import User, Feed, FeedItem


@pytest.mark.asyncio
async def test_unsubscribe(
    user: User,
    feed: Feed,
    feed_items: List[FeedItem],
    repositories: Repositories,
    user_bearer_token,
):
    number_of_subscriptions = feed.number_of_subscriptions
    assert user.number_of_unread_items == 0
    await subscribe_to_feed(feed_id=feed.feed_id.__str__(), authorization=user_bearer_token)
    stored_feed = await repositories.feed_repository.get(feed.feed_id)
    stored_user = await repositories.user_repository.fetch_user_by_email(user.email_address)
    assert stored_feed.number_of_subscriptions == 1 + number_of_subscriptions
    assert stored_user.number_of_unread_items == len(feed_items)
    assert feed.feed_id in stored_user.subscribed_to

    await unsubscribe_from_feed(feed_id=feed.feed_id.__str__(), authorization=user_bearer_token)
    stored_feed = await repositories.feed_repository.get(feed.feed_id)
    stored_user = await repositories.user_repository.fetch_user_by_email(user.email_address)
    assert stored_feed.number_of_subscriptions == number_of_subscriptions
    assert stored_user.number_of_unread_items == 0

    # All items for the user are deleted.
    assert await repositories.news_item_repository.count({}) == 0


@pytest.mark.asyncio
async def test_unsubscribe_while_already_unsubscribed(
    faker: Faker, user: User, feed: Feed, repositories: Repositories, user_bearer_token
):
    number_of_subscriptions = feed.number_of_subscriptions
    assert feed.feed_id not in user.subscribed_to

    await unsubscribe_from_feed(feed_id=feed.feed_id.__str__(), authorization=user_bearer_token)
    stored_feed = await repositories.feed_repository.get(feed.feed_id)
    stored_user = await repositories.user_repository.fetch_user_by_email(user.email_address)
    assert stored_user.subscribed_to == user.subscribed_to
    assert stored_feed.number_of_subscriptions == number_of_subscriptions
