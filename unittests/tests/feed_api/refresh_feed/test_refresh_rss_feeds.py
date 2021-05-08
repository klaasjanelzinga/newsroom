import pytest
from faker import Faker

from api.feed_api import subscribe_to_feed
from core_lib.application_data import Repositories
from core_lib.feed import fetch_feed_information_for, subscribe_user_to_feed, refresh_all_feeds
from core_lib.repositories import User, NewsItem
from tests.conftest import ClientSessionMocker


@pytest.mark.asyncio
async def test_refresh_rss_feed(
    faker: Faker,
    repositories: Repositories,
    client_session_mocker: ClientSessionMocker,
    user: User,
    user_bearer_token: str,
):

    test_url = faker.url()

    # Find the unknown feed. Should fetch 1 feed item.
    client_session_mocker.setup_client_session_for(
        [
            "sample-files/rss_feeds/pitchfork_best_subscribe_fetch.xml",
            "sample-files/rss_feeds/pitchfork_best_first_fetch.xml",
            "sample-files/rss_feeds/pitchfork_best_second_fetch.xml",
            "sample-files/rss_feeds/pitchfork_best_third_fetch.xml",
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
    assert user.number_of_unread_items == 1

    # refresh the feed, with one new item.
    await refresh_all_feeds()
    user = await repositories.user_repository.fetch_user_by_email(user.email_address)
    assert await repositories.feed_item_repository.count({}) == 2
    assert await repositories.news_item_repository.count({}) == 2
    assert user.number_of_unread_items == 2

    # refresh the feed, with the next one, three new items.
    await refresh_all_feeds()
    assert await repositories.news_item_repository.count({}) == 5
    assert await repositories.feed_item_repository.count({}) == 5

    # refresh the feed, with the next one, all new items except the ones already present.
    await refresh_all_feeds()
    assert await repositories.news_item_repository.count({}) == 25
    assert await repositories.feed_item_repository.count({}) == 25


@pytest.mark.asyncio
async def test_refresh_with_duplicate_titles(
    faker: Faker,
    repositories: Repositories,
    client_session_mocker: ClientSessionMocker,
    user: User,
    user_bearer_token: str,
):
    test_url = faker.url()

    # Find the unknown feed. Should fetch all items (8), but there are items with similar titles.
    client_session_mocker.setup_client_session_for(
        [
            "sample-files/rss_feeds/brakdag.xml",
            "sample-files/rss_feeds/brakdag_update_1.xml",
            "sample-files/rss_feeds/brakdag_update_2.xml",
            "sample-files/rss_feeds/brakdag_update_3.xml",
        ]
    )
    feed = await fetch_feed_information_for(repositories.client_session, test_url)
    assert await repositories.feed_item_repository.count({}) == 8
    assert feed is not None

    # subscribe the user, there should be 1 news_item for the user.
    assert user.number_of_unread_items == 0
    await subscribe_to_feed(feed_id=feed.feed_id.__str__(), authorization=user_bearer_token)
    user = await repositories.user_repository.fetch_user_by_email(user.email_address)
    assert feed.feed_id in user.subscribed_to
    assert await repositories.news_item_repository.count({}) == 8
    assert user.number_of_unread_items == 8

    # Check if similarities where correctly flagged within the first refresh.
    count_feed_items = await repositories.feed_item_repository.count(
        {"link": "https://www.gic.nl/nieuws/brand-verwoest-boerderij-aan-stadsweg-in-groningen"}
    )
    assert count_feed_items == 1

    # ----- Next run. The last item is added with a different url but with similar title.
    await refresh_all_feeds()
    user = await repositories.user_repository.fetch_user_by_email(user.email_address)
    assert await repositories.feed_item_repository.count({}) == 9
    assert await repositories.news_item_repository.count({}) == 8  # Created an updated news-item
    assert user.number_of_unread_items == 8

    updated_news_item_json = await repositories.news_item_repository.news_item_collection.find_one(
        {
            "link": "https://www.oogtv.nl/2021/01/uitslaande-brand-in-boerderij-in-ulgersmaborg/?utm_source=rss&utm_medium=rss&utm_campaign=uitslaande-brand-in-boerderij-in-ulgersmaborg"
        }
    )
    news_item = NewsItem.parse_obj(updated_news_item_json)
    assert len(news_item.alternate_title_links) == 1
    assert len(news_item.alternate_links) == 1
    assert len(news_item.alternate_favicons) == 1
    assert news_item.title.startswith("[Updated]")

    # ----- Next run. The last item is added with an identical link and identical title. Nothing happens.
    await refresh_all_feeds()
    user = await repositories.user_repository.fetch_user_by_email(user.email_address)
    assert await repositories.feed_item_repository.count({}) == 9
    assert await repositories.news_item_repository.count({}) == 8
    assert user.number_of_unread_items == 8

    # ----- Next run. The item is added with similar title but with different link.
    await refresh_all_feeds()
    user = await repositories.user_repository.fetch_user_by_email(user.email_address)
    assert await repositories.feed_item_repository.count({}) == 10
    assert await repositories.news_item_repository.count({}) == 8
    assert user.number_of_unread_items == 8
