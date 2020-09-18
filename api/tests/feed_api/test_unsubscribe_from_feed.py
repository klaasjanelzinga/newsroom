from typing import Tuple
from unittest.mock import patch, Mock

import pytest

from api.feed_api import unsubscribe_from_feed
from core_lib.application_data import Repositories
from core_lib.repositories import User, Feed
from tests.conftest import authorization_for


@pytest.mark.asyncio
@patch("api.feed_api.security")
async def test_unsubscribe(security_mock: Mock, subscribed_user: Tuple[User, Feed], repositories: Repositories):
    feed = subscribed_user[1]
    user = subscribed_user[0]

    number_of_subscriptions = feed.number_of_subscriptions
    repositories.mock_feed_repository().get.return_value = feed
    assert feed.feed_id in user.subscribed_to

    with authorization_for(security_mock, subscribed_user[0]):
        response = await unsubscribe_from_feed(feed_id=feed.feed_id, authorization="patched")
        assert feed.feed_id not in response.subscribed_to
        assert feed.number_of_subscriptions == number_of_subscriptions - 1

        # All items for the user are deleted.
        repositories.mock_news_item_repository().delete_user_feed.assert_called_once()
        repositories.mock_subscription_repository().delete_user_feed.assert_called_once()
        assert feed.number_of_subscriptions == 0


@pytest.mark.asyncio
@patch("api.feed_api.security")
async def test_unscubscribe_while_already_unscubscribed(
    security_mock: Mock, user: User, feed: Feed, repositories: Repositories
):
    repositories.mock_feed_repository().get.return_value = feed
    number_of_subscriptions = feed.number_of_subscriptions
    assert feed.feed_id not in user.subscribed_to

    with authorization_for(security_mock, user):
        response = await unsubscribe_from_feed(feed_id=feed.feed_id, authorization="patched")
        assert feed.feed_id not in response.subscribed_to
        assert feed.number_of_subscriptions == number_of_subscriptions

        repositories.mock_subscription_repository().delete_user_feed.assert_not_called()
