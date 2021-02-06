from random import choice
from unittest.mock import MagicMock

import pytest
from faker import Faker
from fastapi import Response

from api.feed_api import subscribe_to_feed, fetch_feed_information_for_url
from api.news_item_api import news_items, read_news_items, mark_as_read, MarkAsReadRequest
from tests.mock_repositories import MockRepositories


@pytest.mark.asyncio
async def test_get_news_items(repositories: MockRepositories, faker: Faker, bearer_token: str):
    test_url = faker.url()

    # Find the unknown feed. Should fetch 1 feed item.
    repositories.mock_client_session_for_files(["sample-files/rss_feeds/pitchfork_best.xml"])
    response = MagicMock(Response)
    feed_response = await fetch_feed_information_for_url(response, test_url, authorization=bearer_token)
    feed = feed_response.feed
    assert repositories.feed_item_repository.count() == 25
    assert feed_response is not None

    # subscribe the user, there should be 20 news-items
    response = await subscribe_to_feed(feed.feed_id, authorization=bearer_token)
    assert repositories.news_item_repository.count() == 25

    # Nothing is read, all is unread.
    just_some_news_item = None
    unread_response = await news_items(fetch_offset=None, authorization=bearer_token)
    assert unread_response.number_of_unread_items == 25
    assert len(unread_response.news_items) == 25
    assert unread_response.token is not None
    just_some_news_item = choice(unread_response.news_items)

    read_items_response = await read_news_items(fetch_offset=None, authorization=bearer_token)
    assert len(read_items_response.news_items) == 0

    # # Mark one item as read
    await mark_as_read(
        mark_as_read_request=MarkAsReadRequest(news_item_ids=[just_some_news_item.news_item_id]),
        authorization=bearer_token,
    )

    # One item is read, rest is unread.
    read_items_response = await read_news_items(fetch_offset=None, authorization=bearer_token)
    assert len(read_items_response.news_items) == 1

    unread_response = await news_items(fetch_offset=None, authorization=bearer_token)
    assert unread_response.number_of_unread_items == 24
    assert len(unread_response.news_items) == 24
