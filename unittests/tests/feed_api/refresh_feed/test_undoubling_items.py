import pytest
from faker import Faker

from api.feed_api import subscribe_to_feed
from core_lib.application_data import Repositories
from core_lib.feed import fetch_feed_information_for, refresh_all_feeds
from core_lib.repositories import User
from tests.conftest import ClientSessionMocker


@pytest.mark.asyncio
async def test_no_undoubling_rss_feed_in_feed_items(
    faker: Faker,
    repositories: Repositories,
    client_session_mocker: ClientSessionMocker,
):

    test_url = faker.url()

    #
    # The file undoubling-events.xml contains:
    # - Christone (1x)
    # - Nina June (1x)
    # - Guus Meeuwis (3x)
    # - Inge van Calkar (2x)
    # - Milkshake festival (2x)
    # - Art of escapism (22x)
    client_session_mocker.setup_client_session_for(
        [
            "sample-files/rss_feeds/undoubling-events.xml",
        ]
    )
    feed = await fetch_feed_information_for(repositories.client_session, test_url)
    assert await repositories.feed_item_repository.count({}) == 31
    assert await repositories.news_item_repository.count({}) == 0  # no subscribers
    assert feed is not None


@pytest.mark.asyncio
async def test_undoubling_rss_feed_when_refreshing(
    faker: Faker,
    repositories: Repositories,
    client_session_mocker: ClientSessionMocker,
    user: User,
    user_bearer_token: str,
):

    test_url = faker.url()

    #
    # The file undoubling-events.xml contains:
    # - Christone (1x)
    # - Nina June (1x)
    # - Guus Meeuwis (3x)
    # - Inge van Calkar (2x)
    # - Milkshake festival (2x)
    # - Art of escapism (22x)
    #
    # The prelude contains the same as Christone with different title, same link.
    client_session_mocker.setup_client_session_for(
        [
            "sample-files/rss_feeds/undoubling-events-prelude.xml",
            "sample-files/rss_feeds/undoubling-events.xml",
        ]
    )
    feed = await fetch_feed_information_for(repositories.client_session, test_url)
    assert await repositories.feed_item_repository.count({}) == 1
    assert feed is not None

    # subscribe the user, there should be 1 news_item for the user.
    assert user.number_of_unread_items == 0
    await subscribe_to_feed(feed_id=feed.feed_id.__str__(), authorization=user_bearer_token)
    user = await repositories.user_repository.fetch_user_by_email(user.email_address)
    assert feed.feed_id in user.subscribed_to
    assert await repositories.news_item_repository.count({}) == 1
    assert await repositories.feed_item_repository.count({}) == 1
    assert user.number_of_unread_items == 1

    # refresh the feed, with one new item.
    await refresh_all_feeds()
    assert await repositories.feed_item_repository.count({}) == 31
    assert await repositories.news_item_repository.count({}) == 6


@pytest.mark.asyncio
async def test_no_undoubling_rss_feed_when_subscribing(
    faker: Faker,
    repositories: Repositories,
    client_session_mocker: ClientSessionMocker,
    user: User,
    user_bearer_token: str,
):

    test_url = faker.url()

    #
    # The file undoubling-events.xml contains:
    # - Christone (1x)
    # - Nina June (1x)
    # - Guus Meeuwis (3x)
    # - Inge van Calkar (2x)
    # - Milkshake festival (2x)
    # - Art of escapism (22x)
    #
    # The prelude contains the same as Christone with different title, same link.
    client_session_mocker.setup_client_session_for(
        [
            "sample-files/rss_feeds/undoubling-events.xml",
        ]
    )
    feed = await fetch_feed_information_for(repositories.client_session, test_url)
    assert await repositories.feed_item_repository.count({}) == 31
    assert feed is not None

    # subscribe the user, there should be 1 news_item for the user.
    assert user.number_of_unread_items == 0
    await subscribe_to_feed(feed_id=feed.feed_id.__str__(), authorization=user_bearer_token)
    user = await repositories.user_repository.fetch_user_by_email(user.email_address)
    assert feed.feed_id in user.subscribed_to
    assert await repositories.news_item_repository.count({}) == 31
    assert await repositories.feed_item_repository.count({}) == 31
    assert user.number_of_unread_items == 31
