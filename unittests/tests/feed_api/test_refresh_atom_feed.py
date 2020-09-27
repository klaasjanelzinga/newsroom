import pytest
from faker import Faker

from core_lib.atom_feed import refresh_atom_feeds
from core_lib.feed import fetch_feed_information_for, subscribe_user_to_feed
from core_lib.repositories import User
from tests.mock_repositories import MockRepositories


@pytest.mark.asyncio
async def test_refresh_atom_feed(faker: Faker, repositories: MockRepositories, user: User):

    test_url = faker.url()

    # Find the unknown feed. Should fetch 1 feed item.
    repositories.mock_client_session_for_files(["tests/atom/fetch_1.xml"])
    feed = await fetch_feed_information_for(repositories.client_session, test_url)
    assert repositories.feed_item_repository.count() == 1
    assert feed is not None

    # subscribe the user, there should be 1 news_item for the user.
    user = subscribe_user_to_feed(user, feed)
    assert feed.feed_id in user.subscribed_to
    assert repositories.news_item_repository.count() == 1

    # refresh the feed, with one new item.
    repositories.mock_client_session_for_files(["tests/atom/fetch_2.xml"])
    await refresh_atom_feeds()
    assert repositories.feed_item_repository.count() == 2
    assert repositories.news_item_repository.count() == 2
