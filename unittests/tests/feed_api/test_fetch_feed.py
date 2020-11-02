from unittest.mock import patch, Mock

import pytest
from faker import Faker

from api.feed_api import get_all_feeds
from core_lib.feed import subscribe_user_to_feed
from core_lib.repositories import User, Feed
from tests.conftest import authorization_for, feed_factory
from tests.mock_repositories import MockRepositories


@pytest.mark.asyncio
@patch("api.feed_api.security")
async def test_fetch_user(security_mock: Mock, repositories: MockRepositories, faker: Faker, user: User, feed: Feed):
    subscribe_user_to_feed(user, feed)
    repositories.feed_repository.upsert(feed_factory(faker))
    with authorization_for(security_mock, user, repositories):
        response = await get_all_feeds(authorization=faker.word())

        assert len(response) == 2
        subscribed_feed = [response_feed for response_feed in response if response_feed.feed.feed_id == feed.feed_id][0]
        assert subscribed_feed.user_is_subscribed
        not_subscribed_feed = [
            response_feed for response_feed in response if response_feed.feed.feed_id != feed.feed_id
        ][0]
        assert not not_subscribed_feed.user_is_subscribed
