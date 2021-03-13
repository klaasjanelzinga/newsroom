from typing import List

import pytest
from faker import Faker

from api.feed_api import subscribe_to_feed
from core_lib.repositories import User, Feed, FeedItem
from tests.mock_repositories import MockRepositories


@pytest.mark.asyncio
async def test_subscribe(
    faker: Faker, user: User, feed: Feed, feed_items: List[FeedItem], repositories: MockRepositories, user_bearer_token
):
    assert feed.feed_id not in user.subscribed_to
    number_of_subscriptions = feed.number_of_subscriptions
    response = await subscribe_to_feed(feed_id=feed.feed_id, authorization=user_bearer_token)

    assert feed.feed_id in repositories.user_repository.fetch_user_by_email(user.email_address).subscribed_to
    assert repositories.news_item_repository.count() == repositories.feed_item_repository.count()

    assert repositories.feed_repository.get(feed.feed_id).number_of_subscriptions == number_of_subscriptions + 1
    assert feed.feed_id in response.subscribed_to
