from typing import Tuple
from unittest.mock import MagicMock

from core_lib.feed import unsubscribe_user_from_feed
from core_lib.repositories import User, Feed


def test_unsubscribe(
    subscribed_user: Tuple[User, Feed], news_item_repository: MagicMock, subscription_repository: MagicMock
):
    feed = subscribed_user[1]
    user = subscribed_user[0]
    assert feed.feed_id in user.subscribed_to
    unsubscribe_user_from_feed(user=user, feed=feed)
    assert feed.feed_id not in user.subscribed_to

    # All items for the user are deleted.
    news_item_repository.delete_user_feed.assert_called_once()
    subscription_repository.delete_user_feed.assert_called_once()
    assert feed.number_of_subscriptions == 0


def test_unscubscribe_while_already_unscubscribed(user: User, feed: Feed, subscription_repository: MagicMock):
    assert feed.feed_id not in user.subscribed_to
    unsubscribe_user_from_feed(user=user, feed=feed)
    assert feed.feed_id not in user.subscribed_to

    subscription_repository.delete_user_feed.assert_not_called()
