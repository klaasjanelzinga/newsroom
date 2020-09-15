from core_lib.application_data import Repositories
from core_lib.feed import subscribe_user_to_feed
from core_lib.repositories import User, Feed


def test_subscribe(user: User, feed: Feed, repositories: Repositories):
    assert feed.feed_id not in user.subscribed_to
    subscribe_user_to_feed(user=user, feed=feed)

    repositories.mock_subscription_repository().upsert.assert_called_once()
    repositories.mock_user_repository().upsert.assert_called_once()
    repositories.mock_feed_repository().upsert.assert_called_once()

    repositories.mock_news_item_repository().upsert_many.assert_called_once()

    assert feed.feed_id in user.subscribed_to
