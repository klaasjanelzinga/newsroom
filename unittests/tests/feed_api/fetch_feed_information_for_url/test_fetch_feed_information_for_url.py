from unittest.mock import MagicMock

import pytest
from faker import Faker

from api.feed_api import fetch_feed_information_for_url, subscribe_to_feed
from core_lib.application_data import Repositories
from core_lib.repositories import Feed, User, FeedItem
from tests.conftest import ClientSessionMocker


@pytest.mark.asyncio
async def test_unsubscribed(faker: Faker, repositories: Repositories, user: User, feed: Feed, user_bearer_token):
    response_mock = MagicMock()

    response = await fetch_feed_information_for_url(
        response=response_mock, url=feed.url, authorization=user_bearer_token
    )

    assert response.feed.feed_id == feed.feed_id
    assert not response.user_is_subscribed
    assert response_mock.status_code == 200


@pytest.mark.asyncio
async def test_subscribed(faker: Faker, repositories: Repositories, user: User, feed: Feed, user_bearer_token):
    response_mock = MagicMock()
    await subscribe_to_feed(feed_id=feed.feed_id.__str__(), authorization=user_bearer_token)

    response = await fetch_feed_information_for_url(
        response=response_mock, url=feed.url, authorization=user_bearer_token
    )
    assert response.user_is_subscribed
    assert response_mock.status_code == 200


@pytest.mark.asyncio
async def test_parse_edge_cases(
    faker: Faker, repositories: Repositories, client_session_mocker: ClientSessionMocker, user: User, user_bearer_token
):
    response_mock = MagicMock()

    client_session_mocker.setup_client_session_for(
        [
            "sample-files/rss_feeds/edge_case.xml",
        ]
    )
    test_url = faker.url()

    response = await fetch_feed_information_for_url(
        response=response_mock, url=test_url, authorization=user_bearer_token
    )
    assert response_mock.status_code == 201
    assert response is not None

    assert response.feed.description is None
    assert await repositories.feed_item_repository.count({}) == 1
    items = await repositories.feed_item_repository.fetch_all_for_feed(response.feed)
    assert items[0].description is None
