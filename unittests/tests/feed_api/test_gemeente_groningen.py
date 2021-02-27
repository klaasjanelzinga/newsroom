import pytest
from faker import Faker

from api.feed_api import subscribe_to_feed
from core_lib.gemeente_groningen import feed_gemeente_groningen
from core_lib.repositories import User, FeedItem
from cron.maintenance_api import do_refresh_all_feeds
from tests.mock_repositories import MockRepositories


@pytest.mark.asyncio
async def test_subscribe_to_gemeente_groningen(
    faker: Faker, repositories: MockRepositories, user: User, user_bearer_token
):
    # 1. Refresh feed so that it exists
    feed = feed_gemeente_groningen
    repositories.mock_client_session_for_files(
        [
            "sample-files/html_sources/gemeente_groningen.html",
            "sample-files/html_sources/gemeente_groningen.html",
            "sample-files/html_sources/gemeente_groningen_2.html",
        ]
    )

    response = await do_refresh_all_feeds()
    assert response is not None
    assert feed.number_of_subscriptions == 0
    assert repositories.feed_item_repository.count() == 0
    assert repositories.news_item_repository.count() == 0

    total_before_subscribe = user.number_of_unread_items
    # 2. Subscribe
    assert feed.feed_id not in user.subscribed_to
    await subscribe_to_feed(feed_id=feed.feed_id, authorization=user_bearer_token)
    assert feed.feed_id in repositories.user_repository.fetch_user_by_email(user.email_address).subscribed_to
    assert repositories.news_item_repository.count() == repositories.feed_item_repository.count()
    assert feed.number_of_items == 0
    assert user.number_of_unread_items == feed.number_of_items
    assert feed.number_of_subscriptions == 1

    # 3. Refresh - let the news flow in.
    response = await do_refresh_all_feeds()
    assert response.number_of_feeds_refreshed == 1
    assert repositories.news_item_repository.count() == 10
    item: FeedItem = repositories.feed_item_repository.fetch_all_for_feed(feed)[0]
    assert item.title == "Glasvezel in gebied Ten Boer"
    assert item.link == "https://gemeente.groningen.nl/actueel/nieuws/glasvezel-in-gebied-ten-boer"
    assert item.created_on is not None
    assert item.published is not None
    assert item.last_seen is not None

    # 3. Refresh again
    response = await do_refresh_all_feeds()
    assert response.number_of_feeds_refreshed == 1
    assert repositories.news_item_repository.count() == 20
