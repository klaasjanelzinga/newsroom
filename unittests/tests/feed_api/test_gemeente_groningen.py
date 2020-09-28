from unittest.mock import Mock, patch

import pytest
from faker import Faker

from api.feed_api import subscribe_to_feed
from core_lib.gemeente_groningen import feed_gemeente_groningen
from core_lib.html_feed import refresh_html_feed, refresh_html_feeds
from core_lib.repositories import User, FeedItem, FeedSourceType
from tests.conftest import authorization_for
from tests.mock_repositories import MockRepositories


@pytest.mark.asyncio
async def test_refresh_gemeente_groningen(faker: Faker, repositories: MockRepositories, user: User):
    html_gemeente_groningen = "tests/html_sources/gemeente_groningen.html"
    feed = feed_gemeente_groningen

    repositories.mock_client_session_for_files([html_gemeente_groningen])

    response = await refresh_html_feed(feed=feed, session=repositories.client_session)
    assert response is not None

    assert response.feed_id == feed.feed_id
    assert response.feed_source_type == FeedSourceType.HTML.name
    assert repositories.feed_item_repository.count() == 10
    item: FeedItem = repositories.feed_item_repository.fetch_all_for_feed(feed)[0]
    assert item.title == "Glasvezel in gebied Ten Boer"
    assert item.link == "https://gemeente.groningen.nl/actueel/nieuws/glasvezel-in-gebied-ten-boer"
    assert item.created_on is not None
    assert item.published is not None
    assert item.last_seen is not None


@pytest.mark.asyncio
@patch("api.feed_api.security")
async def test_subscribe_to_gemeente_groningen(
    security_mock: Mock, faker: Faker, repositories: MockRepositories, user: User
):
    # 1. Refresh feed so that it exists
    html_gemeente_groningen = "tests/html_sources/gemeente_groningen.html"
    feed = feed_gemeente_groningen

    repositories.mock_client_session_for_files([html_gemeente_groningen])

    response = await refresh_html_feeds()
    assert response is not None

    # 2. Subscribe
    with authorization_for(security_mock, user, repositories):

        assert feed.feed_id not in user.subscribed_to
        response = await subscribe_to_feed(feed_id=feed.feed_id, authorization=faker.word())
        assert feed.feed_id in repositories.user_repository.fetch_user_by_email(user.email).subscribed_to
        assert repositories.news_item_repository.count() == repositories.feed_item_repository.count()
