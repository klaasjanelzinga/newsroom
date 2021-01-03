from datetime import datetime
from typing import List, Optional

from core_lib.application_data import repositories
from core_lib.repositories import Feed, FeedItem, User, NewsItem, RefreshResult


def upsert_new_items_for_feed(feed: Feed, updated_feed: Feed, feed_items_from_rss: List[FeedItem]) -> int:
    """
    Upload new items as feed item and news item for users.

    - Upload all the feed-items if feed item did not exist yet.
    - If feed-item exists, tick the last_seen timestamp.
    - For all subscribed users, make news items and upsert new feed items.
    - Set number_of_items, last_fetched and mutable details for the feed itself.

    returns: Number of items updated for the feed.
    """
    current_feed_items = repositories.feed_item_repository.fetch_all_for_feed(feed)
    new_feed_items = []
    updated_feed_items = []
    for new_item in feed_items_from_rss:
        current_item = [item for item in current_feed_items if item.link == new_item.link]
        if len(current_item) == 0:
            new_feed_items.append(new_item)
        elif len(current_item) == 1:
            current_item[0].last_seen = datetime.utcnow()
            updated_feed_items.append(current_item[0])
    repositories.feed_item_repository.upsert_many(new_feed_items)
    repositories.feed_item_repository.upsert_many(updated_feed_items)
    # splice to subscribed users
    users = repositories.user_repository.fetch_subscribed_to(feed)
    for user in users:
        repositories.news_item_repository.upsert_many(news_items_from_feed_items(new_feed_items, feed, user))
    # Update information in feed item with latest information from the url.
    feed.last_fetched = datetime.utcnow()
    feed.description = updated_feed.description
    feed.title = updated_feed.title
    feed.number_of_items = feed.number_of_items + len(new_feed_items)
    repositories.feed_repository.upsert(feed)
    return len(new_feed_items)


def update_users_unread_count_with_refresh_results(refresh_results: List[Optional[RefreshResult]]) -> None:
    """
    Update the count of unread items per feed per subscribed user.
    """
    for refresh_result in [result for result in refresh_results if result is not None]:
        subscribed_users = repositories.user_repository.fetch_subscribed_to(refresh_result.feed)
        for user in subscribed_users:
            user.number_of_unread_items += refresh_result.number_of_items
        repositories.user_repository.upsert_many(subscribed_users)


def news_items_from_feed_items(feed_items: List[FeedItem], feed: Feed, user: User) -> List[NewsItem]:
    return [news_item_from_feed_item(feed_item, feed, user) for feed_item in feed_items]


def news_item_from_feed_item(feed_item: FeedItem, feed: Feed, user: User) -> NewsItem:
    return NewsItem(
        feed_id=feed_item.feed_id,
        user_id=user.user_id,
        feed_item_id=feed_item.feed_item_id,
        feed_title=feed.title,
        title=feed_item.title,
        description=feed_item.description,
        link=feed_item.link,
        published=feed_item.published or datetime.utcnow(),
    )
