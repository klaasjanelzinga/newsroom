import pytest
from faker import Faker

from api.feed_api import subscribe_to_feed
from core_lib.application_data import Repositories
from core_lib.feed import fetch_feed_information_for, subscribe_user_to_feed, refresh_all_feeds
from core_lib.repositories import User
from tests.conftest import ClientSessionMocker


@pytest.mark.asyncio
async def test_refresh_rdf_feed(
    faker: Faker,
    repositories: Repositories,
    client_session_mocker: ClientSessionMocker,
    user: User,
    user_bearer_token: str,
):

    test_url = faker.url()

    # Find the unknown feed. Should fetch 1 feed item.
    client_session_mocker.setup_client_session_for(
        ["sample-files/rdf_sources/slashdot_1.xml", "sample-files/rdf_sources/slashdot_2.xml"]
    )
    feed = await fetch_feed_information_for(repositories.client_session, test_url)
    assert await repositories.feed_item_repository.count({}) == 2
    assert feed is not None

    # subscribe the user, there should be 1 news_item for the user.
    await subscribe_to_feed(feed_id=feed.feed_id.__str__(), authorization=user_bearer_token)
    user = await repositories.user_repository.fetch_user_by_email(user.email_address)
    assert feed.feed_id in user.subscribed_to
    assert await repositories.news_item_repository.count({}) == 2
    assert user.number_of_unread_items == 2

    # refresh the feed, with one new item.
    await refresh_all_feeds()
    user = await repositories.user_repository.fetch_user_by_email(user.email_address)
    assert await repositories.feed_item_repository.count({}) == 15
    assert await repositories.news_item_repository.count({}) == 15
    assert user.number_of_unread_items == 15
