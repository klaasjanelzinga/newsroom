from random import choice

import pytest
from faker import Faker

from api.news_item_api import news_items, read_news_items, mark_as_read, MarkAsReadRequest
from core_lib.application_data import Repositories
from core_lib.repositories import User


@pytest.mark.asyncio
async def test_get_news_items(
    repositories: Repositories, faker: Faker, user_with_subscription_to_feed: User, user_bearer_token: str
):

    # Nothing is read, all is unread.
    unread_response = await news_items(authorization=user_bearer_token)
    assert unread_response.number_of_unread_items == 25
    assert len(unread_response.news_items) == 25
    just_some_news_item = choice(unread_response.news_items)

    read_items_response = await read_news_items(fetch_offset=0, authorization=user_bearer_token)
    assert len(read_items_response.news_items) == 0

    # # Mark one item as read
    await mark_as_read(
        mark_as_read_request=MarkAsReadRequest(news_item_ids=[just_some_news_item.news_item_id.__str__()]),
        authorization=user_bearer_token,
    )

    # One item is read, rest is unread.
    read_items_response = await read_news_items(fetch_offset=0, authorization=user_bearer_token)
    assert len(read_items_response.news_items) == 1

    unread_response = await news_items(authorization=user_bearer_token)
    assert unread_response.number_of_unread_items == 24
    assert len(unread_response.news_items) == 24
