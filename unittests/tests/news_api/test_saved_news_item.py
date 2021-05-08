from random import choice

import pytest

from api.news_item_api import news_items
from api.saved_items_api import save_news_item, SaveNewsItemRequest, get_saved_news_items, delete_saved_news_item
from core_lib.application_data import Repositories
from core_lib.repositories import User, SavedNewsItem


@pytest.mark.asyncio
async def test_save_news_item(repositories: Repositories, user_with_subscription_to_feed: User, user_bearer_token: str):
    unread_response = await news_items(fetch_offset=0, authorization=user_bearer_token)
    just_some_news_item = choice(unread_response.news_items)

    response = await save_news_item(
        SaveNewsItemRequest(news_item_id=just_some_news_item.news_item_id.__str__()), authorization=user_bearer_token
    )
    assert response is not None
    assert await repositories.saved_news_item_repository.count({}) == 1
    saved_item: SavedNewsItem = await repositories.saved_news_item_repository.fetch_by_id(response.saved_news_item_id)

    assert (await repositories.news_item_repository.fetch_by_id(just_some_news_item.news_item_id)).is_saved
    assert (
        await repositories.news_item_repository.fetch_by_id(just_some_news_item.news_item_id)
    ).saved_news_item_id == saved_item.saved_news_item_id

    assert just_some_news_item.feed_id == saved_item.feed_id
    assert just_some_news_item.user_id == user_with_subscription_to_feed.user_id
    assert just_some_news_item.feed_item_id == saved_item.feed_item_id
    assert just_some_news_item.title == saved_item.title
    assert just_some_news_item.description == saved_item.description
    assert just_some_news_item.created_on == saved_item.created_on
    assert just_some_news_item.alternate_links == saved_item.alternate_links
    assert just_some_news_item.alternate_favicons == saved_item.alternate_favicons
    assert just_some_news_item.alternate_title_links == saved_item.alternate_title_links
    assert just_some_news_item.published == saved_item.published
    assert just_some_news_item.link == saved_item.link
    assert just_some_news_item.favicon == saved_item.favicon
    assert just_some_news_item.feed_title == saved_item.feed_title


@pytest.mark.asyncio
async def test_save_fetch_and_remove_from_saved(
    repositories: Repositories, user_with_subscription_to_feed: User, user_bearer_token: str
):
    unread_response = await news_items(fetch_offset=0, authorization=user_bearer_token)
    just_some_news_item = choice(unread_response.news_items)
    news_item_id = just_some_news_item.news_item_id

    response = await save_news_item(
        save_news_request=SaveNewsItemRequest(news_item_id=just_some_news_item.news_item_id.__str__()),
        authorization=user_bearer_token,
    )
    assert response is not None
    saved_news_item_id = response.saved_news_item_id
    assert (await repositories.news_item_repository.fetch_by_id(news_item_id)).is_saved
    assert (await repositories.news_item_repository.fetch_by_id(news_item_id)).saved_news_item_id is not None

    get_response = await get_saved_news_items(fetch_offset=0, fetch_limit=30, authorization=user_bearer_token)
    assert len(get_response.items) == 1
    assert await repositories.saved_news_item_repository.count({}) == 1
    assert get_response.items[0].saved_news_item_id.__str__() == saved_news_item_id

    await delete_saved_news_item(saved_news_item_id, user_bearer_token)

    get_response = await get_saved_news_items(fetch_offset=0, fetch_limit=30, authorization=user_bearer_token)
    assert len(get_response.items) == 0
    assert await repositories.saved_news_item_repository.count({}) == 0
    assert not (await repositories.news_item_repository.fetch_by_id(news_item_id)).is_saved
    assert (await repositories.news_item_repository.fetch_by_id(news_item_id)).saved_news_item_id is None
