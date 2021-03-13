import pytest
from faker import Faker

from core_lib.feed import fetch_feed_information_for, subscribe_user_to_feed, refresh_all_feeds
from core_lib.repositories import User
from tests.mock_repositories import MockRepositories


@pytest.mark.asyncio
async def test_refresh_rss_feed(faker: Faker, repositories: MockRepositories, user: User):

    test_url = faker.url()

    # Find the unknown feed. Should fetch 1 feed item.
    repositories.mock_client_session_for_files(["sample-files/rss_feeds/pitchfork_best_subscribe_fetch.xml"])
    feed = await fetch_feed_information_for(repositories.client_session, test_url)
    assert repositories.feed_item_repository.count() == 1
    assert feed is not None

    # subscribe the user, there should be 1 news_item for the user.
    assert user.number_of_unread_items == 0
    user = subscribe_user_to_feed(user, feed)
    assert feed.feed_id in user.subscribed_to
    assert repositories.news_item_repository.count() == 1
    assert user.number_of_unread_items == 1

    # refresh the feed, with one new item.
    repositories.mock_client_session_for_files(["sample-files/rss_feeds/pitchfork_best_first_fetch.xml"])
    await refresh_all_feeds(False)
    assert repositories.feed_item_repository.count() == 2
    assert repositories.news_item_repository.count() == 2
    assert user.number_of_unread_items == 2

    # refresh the feed, with the next one, three new items.
    repositories.mock_client_session_for_files(["sample-files/rss_feeds/pitchfork_best_second_fetch.xml"])
    await refresh_all_feeds(False)
    assert repositories.news_item_repository.count() == 5
    assert repositories.feed_item_repository.count() == 5

    # refresh the feed, with the next one, all new items except the ones already present.
    repositories.mock_client_session_for_files(["sample-files/rss_feeds/pitchfork_best_third_fetch.xml"])
    await refresh_all_feeds(False)
    assert repositories.news_item_repository.count() == 25
    assert repositories.feed_item_repository.count() == 25


@pytest.mark.asyncio
async def test_refresh_with_duplicate_titles(faker: Faker, repositories: MockRepositories, user: User):
    test_url = faker.url()

    # Find the unknown feed. Should fetch all items (8), but there are items with similar titles.
    repositories.mock_client_session_for_files(["sample-files/rss_feeds/brakdag.xml"])
    feed = await fetch_feed_information_for(repositories.client_session, test_url)
    assert repositories.feed_item_repository.count() == 8
    assert feed is not None

    # subscribe the user, there should be 1 news_item for the user.
    assert user.number_of_unread_items == 0
    user = subscribe_user_to_feed(user, feed)
    assert feed.feed_id in user.subscribed_to
    assert repositories.news_item_repository.count() == 8
    assert user.number_of_unread_items == 8

    # Check if similarities where correctly flagged within the first refresh.
    feed_items = [
        item
        for item in repositories.feed_item_repository.store.values()
        if item.link == "https://www.gic.nl/nieuws/brand-verwoest-boerderij-aan-stadsweg-in-groningen"
    ]
    assert len(feed_items) == 1

    # ----- Next run. The last item is added with a different url but with similar title.
    repositories.mock_client_session_for_files(["sample-files/rss_feeds/brakdag_update_1.xml"])
    await refresh_all_feeds(False)
    assert repositories.feed_item_repository.count() == 9
    assert repositories.news_item_repository.count() == 8  # Created an updated news-item
    assert user.number_of_unread_items == 8
    updated_news_items = [
        item
        for item in repositories.news_item_repository.store.values()
        if item.link.startswith("https://www.oogtv.nl/2021/01/uitslaande-brand-in-boerderij-in-ulgersmaborg/")
    ]
    assert len(updated_news_items) == 1
    assert len(updated_news_items[0].alternate_title_links) == 1
    assert len(updated_news_items[0].alternate_links) == 1
    assert len(updated_news_items[0].alternate_favicons) == 1
    assert updated_news_items[0].title.startswith("[Updated]")

    # ----- Next run. The last item is added with an identical link and identical title. Nothing happens.
    repositories.mock_client_session_for_files(["sample-files/rss_feeds/brakdag_update_2.xml"])
    await refresh_all_feeds(False)
    assert repositories.feed_item_repository.count() == 9
    assert repositories.news_item_repository.count() == 8
    assert user.number_of_unread_items == 8

    # ----- Next run. The item is added with similar title but with different link.
    repositories.mock_client_session_for_files(["sample-files/rss_feeds/brakdag_update_3.xml"])
    await refresh_all_feeds(False)
    assert repositories.feed_item_repository.count() == 10
    assert repositories.news_item_repository.count() == 8
    assert user.number_of_unread_items == 8
