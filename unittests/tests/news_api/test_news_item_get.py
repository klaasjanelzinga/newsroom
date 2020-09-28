from random import choice
from typing import List
from unittest.mock import patch, Mock

import pytest
from faker import Faker

from api.feed_api import subscribe_to_feed
from api.news_item_api import news_items, read_news_items, mark_as_read, MarkAsReadRequest
from core_lib.feed import fetch_feed_information_for, subscribe_user_to_feed
from core_lib.repositories import User
from tests.conftest import authorization_for
from tests.mock_repositories import MockRepositories


@pytest.mark.asyncio
@patch("api.news_item_api.security")
@patch("api.feed_api.security")
async def test_get_news_items(
    security_mock: Mock, security_mock_news_item: Mock, repositories: MockRepositories, faker: Faker, user: User
):
    test_url = faker.url()

    # Find the unknown feed. Should fetch 1 feed item.
    repositories.mock_client_session_for_files(["tests/sample_rss_feeds/pitchfork_best.xml"])
    feed = await fetch_feed_information_for(repositories.client_session, test_url)
    assert repositories.feed_item_repository.count() == 25
    assert feed is not None

    # subscribe the user, there should be 20 news-items
    with authorization_for(security_mock, user, repositories):
        response = await subscribe_to_feed(feed.feed_id, authorization=faker.word())
        assert repositories.news_item_repository.count() == 25

    # Nothing is read, all is unread.
    just_some_news_item = None
    with authorization_for(security_mock_news_item, user, repositories):
        unread_response = await news_items(fetch_offset=None, authorization=faker.word())
        assert len(unread_response.news_items) == 25
        assert unread_response.token is not None
        just_some_news_item = choice(unread_response.news_items)

    with authorization_for(security_mock_news_item, user, repositories):
        read_items_response = await read_news_items(fetch_offset=None, authorization=faker.word())
        assert len(read_items_response.news_items) == 0

    # Mark one item as read
    with authorization_for(security_mock_news_item, user, repositories):
        await mark_as_read(mark_as_read_request=MarkAsReadRequest(news_item_ids=[just_some_news_item.news_item_id]))

    # One item is read, rest is unread.
    with authorization_for(security_mock_news_item, user, repositories):
        read_items_response = await read_news_items(fetch_offset=None, authorization=faker.word())
        assert len(read_items_response.news_items) == 1

    with authorization_for(security_mock_news_item, user, repositories):
        unread_response = await news_items(fetch_offset=None, authorization=faker.word())
        assert len(unread_response.news_items) == 24
