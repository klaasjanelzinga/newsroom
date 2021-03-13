from unittest.mock import MagicMock

import pytest
from faker import Faker

from api.feed_api import fetch_feed_information_for_url, subscribe_to_feed
from core_lib.repositories import Feed, User, FeedItem
from tests.mock_repositories import MockRepositories


@pytest.mark.asyncio
async def test_unsubscribed(faker: Faker, repositories: MockRepositories, user: User, feed: Feed, user_bearer_token):
    response_mock = MagicMock()

    response = await fetch_feed_information_for_url(
        response=response_mock, url=feed.url, authorization=user_bearer_token
    )

    assert response.feed.feed_id == feed.feed_id
    assert not response.user_is_subscribed
    assert response_mock.status_code == 200


@pytest.mark.asyncio
async def test_subscribed(faker: Faker, repositories: MockRepositories, user: User, feed: Feed, user_bearer_token):
    response_mock = MagicMock()
    await subscribe_to_feed(feed_id=feed.feed_id, authorization=user_bearer_token)

    response = await fetch_feed_information_for_url(
        response=response_mock, url=feed.url, authorization=user_bearer_token
    )
    assert response.user_is_subscribed
    assert response_mock.status_code == 200


@pytest.mark.asyncio
async def test_parse_edge_cases(faker: Faker, repositories: MockRepositories, user: User, user_bearer_token):
    response_mock = MagicMock()

    xml_test_files = [
        "sample-files/rss_feeds/edge_case.xml",
    ]
    repositories.mock_client_session_for_files(xml_test_files)
    test_url = faker.url()

    response = await fetch_feed_information_for_url(
        response=response_mock, url=test_url, authorization=user_bearer_token
    )
    assert response_mock.status_code == 201
    assert response is not None

    assert response.feed.description is None
    assert repositories.feed_item_repository.count() == 1
    item: FeedItem = repositories.feed_item_repository.fetch_all_for_feed(response.feed)[0]
    assert item.description is None
