import pytest
from faker import Faker

from core_lib.application_data import Repositories
from core_lib.feed import refresh_rss_feeds, fetch_feed_information_for, subscribe_user_to_feed
from core_lib.repositories import User


@pytest.mark.asyncio
async def test_parse_sample_feeds(faker: Faker, repositories: Repositories, user: User):

    test_url = faker.url()

    repositories.mock_feed_repository().find_by_url.return_value = None
    # with authorization_for(security_mock, user):

    # Find the unknown feed. Should fetch 1 feed item.
    repositories.feed_repository.find_by_url.return_value = None
    repositories.mock_client_session_for_files(["tests/sample_rss_feeds/pitchfork_best_subscribe_fetch.xml"])
    feed = await fetch_feed_information_for(repositories.client_session, test_url)
    upserted_feed_items = repositories.mock_feed_item_repository().upsert_many.call_args[0][0]
    assert len(upserted_feed_items) == 1
    assert feed is not None

    # subscribe the user, there should be 1 news_item for the user.
    repositories.reset_mocks()
    repositories.mock_feed_item_repository().fetch_all_for_feed.return_value = upserted_feed_items
    user = subscribe_user_to_feed(user, feed)
    assert feed.feed_id in user.subscribed_to
    news_items = repositories.mock_news_item_repository().upsert_many.call_args[0][0]
    assert len(news_items) == 1

    # refresh the feed, with one new item.
    repositories.reset_mocks()
    repositories.mock_client_session_for_files(["tests/sample_rss_feeds/pitchfork_best_first_fetch.xml"])
    repositories.mock_feed_repository().get_active_feeds.return_value = [feed]
    repositories.mock_user_repository().fetch_subscribed_to.return_value = [user]
    repositories.mock_feed_item_repository().fetch_all_for_feed.return_value = upserted_feed_items

    await refresh_rss_feeds()
    repositories.mock_news_item_repository().upsert_many.assert_called_once()
    repositories.mock_feed_item_repository().upsert_many.assert_called_once()
    news_items = repositories.mock_news_item_repository().upsert_many.call_args[0][0]
    upserted_feed_items.extend(repositories.mock_feed_item_repository().upsert_many.call_args[0][0])
    assert len(news_items) == 1

    # refresh the feed, with the next one, three new items.
    repositories.reset_mocks()
    repositories.mock_client_session_for_files(["tests/sample_rss_feeds/pitchfork_best_second_fetch.xml"])
    repositories.mock_feed_repository().get_active_feeds.return_value = [feed]
    repositories.mock_user_repository().fetch_subscribed_to.return_value = [user]
    repositories.mock_feed_item_repository().fetch_all_for_feed.return_value = upserted_feed_items
    await refresh_rss_feeds()
    news_items = repositories.mock_news_item_repository().upsert_many.call_args[0][0]
    repositories.mock_feed_item_repository().upsert_many.assert_called_once()
    upserted_feed_items.extend(repositories.mock_feed_item_repository().upsert_many.call_args[0][0])
    assert len(news_items) == 3

    # refresh the feed, with the next one, all new items except the ones already present.
    repositories.reset_mocks()
    repositories.mock_client_session_for_files(["tests/sample_rss_feeds/pitchfork_best_third_fetch.xml"])
    repositories.mock_feed_repository().get_active_feeds.return_value = [feed]
    repositories.mock_user_repository().fetch_subscribed_to.return_value = [user]
    repositories.mock_feed_item_repository().fetch_all_for_feed.return_value = upserted_feed_items

    await refresh_rss_feeds()
    news_items = repositories.mock_news_item_repository().upsert_many.call_args[0][0]
    assert len(news_items) == 20
