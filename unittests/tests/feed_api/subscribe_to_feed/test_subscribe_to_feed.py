from typing import List

import pytest
from faker import Faker

from api.feed_api import subscribe_to_feed
from core_lib.application_data import Repositories
from core_lib.repositories import User, Feed, FeedItem


@pytest.mark.asyncio
async def test_subscribe(
    faker: Faker, user: User, feed: Feed, feed_items: List[FeedItem], repositories: Repositories, user_bearer_token
):
    assert feed.feed_id not in user.subscribed_to
    number_of_subscriptions = feed.number_of_subscriptions
    await subscribe_to_feed(feed_id=feed.feed_id.__str__(), authorization=user_bearer_token)

    stored_feed = await repositories.feed_repository.get(feed.feed_id)
    stored_user = await repositories.user_repository.fetch_user_by_email(user.email_address)

    assert feed.feed_id in stored_user.subscribed_to
    assert await repositories.news_item_repository.count({}) == await repositories.feed_item_repository.count({})

    assert stored_feed.number_of_subscriptions == number_of_subscriptions + 1
