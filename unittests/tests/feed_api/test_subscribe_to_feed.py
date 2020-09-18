from unittest.mock import patch, Mock

import pytest

from api.feed_api import subscribe_to_feed
from core_lib.application_data import Repositories
from core_lib.repositories import User, Feed
from tests.conftest import authorization_for


@pytest.mark.asyncio
@patch("api.feed_api.security")
async def test_subscribe(security_mock: Mock, user: User, feed: Feed, repositories: Repositories):
    with authorization_for(security_mock, user):

        assert feed.feed_id not in user.subscribed_to
        repositories.mock_feed_repository().get.return_value = feed
        response = await subscribe_to_feed(feed_id=feed.feed_id, authorization="dummy")

        repositories.mock_subscription_repository().upsert.assert_called_once()
        repositories.mock_user_repository().upsert.assert_called_once()
        repositories.mock_feed_repository().upsert.assert_called_once()

        repositories.mock_news_item_repository().upsert_many.assert_called_once()

        assert feed.feed_id in response.subscribed_to
