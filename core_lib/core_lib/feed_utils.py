import difflib
import re
from datetime import datetime
from typing import List, Optional
from urllib.parse import urlparse

import pytz

from core_lib.application_data import repositories
from core_lib.repositories import Feed, FeedItem, User, NewsItem, RefreshResult


def now_in_utc() -> datetime:
    return datetime.now(tz=pytz.utc)


def are_titles_similar(title_1: str, title_2: str) -> bool:
    title_1 = re.sub(r"\[.*]", "", title_1)
    title_2 = re.sub(r"\[.*]", "", title_2)
    return len(title_1) > 10 and difflib.SequenceMatcher(None, title_1, title_2).ratio() > 0.516


def upsert_new_items_for_feed(feed: Feed, updated_feed: Feed, feed_items_from_rss: List[FeedItem]) -> int:
    """
    Upload new items as feed item and news item for users.

    - Upload all the feed-items if feed item did not exist yet.
    - If feed-item exists, tick the last_seen timestamp.
    - For all subscribed users, make news items and upsert new feed items.
    - Set number_of_items, last_fetched and mutable details for the feed itself.

    returns: Number of new NewsItems created.
    """
    current_feed_items = repositories.feed_item_repository.fetch_all_for_feed(feed)
    new_feed_items: List[FeedItem] = []  # new feed_items that will be inserted.
    updated_feed_items: List[FeedItem] = []  # updated feed_items that will be updated.
    updated_feed_items_with_news: List[FeedItem] = []  # updated feed_items that contain relevant information for news.
    for new_item in feed_items_from_rss:
        items_with_similar_titles = [
            item for item in current_feed_items if are_titles_similar(item.title, new_item.title)
        ]
        items_with_same_link = [item for item in current_feed_items if item.link == new_item.link]

        # Items with the same link, we already had that one. Update last_seen timestamp.
        if len(items_with_same_link) == 1:
            items_with_same_link[0].last_seen = now_in_utc()
            updated_feed_items.append(items_with_same_link[0])

        # Items with different link, but similarities in the title. Update last_seen of all and register alternate url.
        elif len(items_with_similar_titles) > 0:
            for item in items_with_similar_titles:
                item.last_seen = datetime.utcnow()
                if new_item.link not in item.alternate_links:
                    item.append_alternate(link=new_item.link, title=new_item.title)
                    item.title = f"[Updated] {item.title}" if "[Updated]" not in item.title else item.title
                    if item.feed_item_id not in [n.feed_item_id for n in new_feed_items]:
                        updated_feed_items_with_news.append(item)
                updated_feed_items.append(item)

        # Or just insert in the store
        elif len(items_with_same_link) == 0 and len(items_with_same_link) == 0:
            new_feed_items.append(new_item)
            current_feed_items.append(new_item)  # Make sure to include new items in this run for the seqmatcher.

    # Upsert the new and updated feed_items.
    repositories.feed_item_repository.upsert_many(new_feed_items)
    repositories.feed_item_repository.upsert_many(updated_feed_items)
    # Splice to subscribed users. Make news_items for new feed_items and for feed_items with relevant updates.
    users = repositories.user_repository.fetch_subscribed_to(feed)
    for user in users:
        repositories.news_item_repository.upsert_many(news_items_from_feed_items(new_feed_items, feed, user))
        repositories.news_item_repository.upsert_many(
            news_items_from_feed_items(updated_feed_items_with_news, feed, user)
        )
    # Update information in feed item with latest information from the url.
    feed.last_fetched = datetime.utcnow()
    feed.description = updated_feed.description
    feed.title = updated_feed.title
    feed.number_of_items = feed.number_of_items + len(new_feed_items)
    repositories.feed_repository.upsert(feed)
    return len(new_feed_items) + len(updated_feed_items_with_news)


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


def determine_favicon_link(feed_item: FeedItem, feed: Feed) -> str:
    feed_item_link_domain = urlparse(feed_item.link).netloc
    feed_domain = urlparse(feed.url).netloc
    if feed_item_link_domain == feed_domain:
        return feed.image_url or f"https://{feed_domain}/favicon.ico"
    if feed_item_link_domain == "www.sikkom.nl":
        return "https://www.sikkom.nl/wp-content/themes/sikkom-v3/img/favicon.ico"
    if feed_item_link_domain == "www.gic.nl":
        return "https://www.gic.nl/img/favicon.ico"
    if feed_item_link_domain == "www.rtvnoord.nl":
        return "https://www.rtvnoord.nl/Content/Images/noord/favicon.ico"
    return f"https://{feed_item_link_domain}/favicon.ico"


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
        alternate_links=feed_item.alternate_links,
        alternate_title_links=feed_item.alternate_title_links,
        favicon=determine_favicon_link(feed_item, feed),
    )
