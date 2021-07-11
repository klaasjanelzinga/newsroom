from datetime import datetime, timedelta
import difflib
import re
from typing import Dict, List
from urllib.parse import urlparse

import pytz

from core_lib.application_data import repositories
from core_lib.repositories import Feed, FeedItem, FeedSourceType, NewsItem, User
from core_lib.utils import now_in_utc


def are_titles_similar(title_1: str, title_2: str) -> bool:
    title_1 = re.sub(r"\[.*?]", "", title_1)
    title_2 = re.sub(r"\[.*?]", "", title_2)
    return len(title_1) > 10 and difflib.SequenceMatcher(None, title_1, title_2).ratio() > 0.516


def item_is_still_relevant(item: FeedItem) -> bool:
    try:
        return item.created_on > (datetime.now(tz=pytz.utc) - timedelta(hours=18))
    except TypeError:
        return item.created_on > (datetime.now() - timedelta(hours=18))


async def upsert_new_feed_items_for_feed(feed: Feed, feed_items: List[FeedItem]) -> int:
    current_feed_item_links = [
        feed_item.link for feed_item in await repositories().feed_item_repository.fetch_all_for_feed(feed)
    ]
    new_feed_items = [
        new_feed_item for new_feed_item in feed_items if new_feed_item.link not in current_feed_item_links
    ]
    await repositories().feed_item_repository.upsert_many(new_feed_items)
    return len(new_feed_items)


class UpdateResult:
    def __init__(self) -> None:
        self.user_to_number_new_items_map: Dict[str, int] = {}

    def __repr__(self) -> str:
        return str(self.user_to_number_new_items_map)

    def add(self, user_id: str, new_items: int) -> None:
        if user_id not in self.user_to_number_new_items_map:
            self.user_to_number_new_items_map[user_id] = 0
        self.user_to_number_new_items_map[user_id] = self.user_to_number_new_items_map[user_id] + new_items


async def upsert_new_items_for_feed(
    feed: Feed, updated_feed: Feed, feed_items_from_rss: List[FeedItem]
) -> UpdateResult:
    """
    Upload new items as feed item and news item for users.

    - Upload all the feed-items if feed item did not exist yet.
    - If feed-item exists, tick the last_seen timestamp.
    - For all subscribed users, make news items and upsert new feed items.
    - Set number_of_items, last_fetched and mutable details for the feed itself.

    returns: Number of new NewsItems created.
    """
    current_feed_items = await repositories().feed_item_repository.fetch_all_for_feed(feed)
    subscribed_users = await repositories().user_repository.fetch_subscribed_to(feed)

    updated_feed_items: List[FeedItem] = []  # updated feed_items that will be updated.
    new_feed_items: List[FeedItem] = []  # new feed_items that will be inserted.
    new_news_items: List[NewsItem] = []  # news items that will be inserted.
    updated_news_items: List[NewsItem] = []  # news items that are updated.
    update_result = UpdateResult()

    for user in subscribed_users:
        number_of_new_items = 0
        current_news_items = await repositories().news_item_repository.fetch_all_non_read_for_feed(feed, user)
        for new_feed_item in feed_items_from_rss:
            feed_items_with_same_link = [item for item in current_feed_items if item.link == new_feed_item.link]
            if len(feed_items_with_same_link) > 0:  # We have seen this item already, update last seen.
                for feed_item in feed_items_with_same_link:
                    feed_item.last_seen = now_in_utc()
                updated_feed_items.extend(feed_items_with_same_link)
            else:
                # New feed item.
                new_feed_items.append(new_feed_item)
                current_feed_items.append(new_feed_item)

                # Check if there is already a similar news item to flag alternates.
                news_items_similar_titles = [
                    news_item
                    for news_item in current_news_items
                    if are_titles_similar(title_1=news_item.title, title_2=new_feed_item.title)
                ]
                # If no similar news items, just insert new news item and feed item, else update existing news item.
                if len(news_items_similar_titles) == 0:
                    new_news_item = news_item_from_feed_item(new_feed_item, feed, user)
                    new_news_items.append(new_news_item)
                    number_of_new_items += 1
                    current_news_items.append(new_news_item)
                else:
                    for existing_news_item in news_items_similar_titles:
                        existing_news_item.append_alternate(
                            new_feed_item.link, new_feed_item.title, determine_favicon_link(new_feed_item)
                        )
                        existing_news_item.published = new_feed_item.published or now_in_utc()
                        updated_news_items.append(existing_news_item)
        update_result.add(user.user_id, number_of_new_items)

    # Upsert the new and updated feed_items.
    await repositories().feed_item_repository.upsert_many(new_feed_items)
    await repositories().feed_item_repository.upsert_many(updated_feed_items)
    await repositories().news_item_repository.upsert_many(new_news_items)
    await repositories().news_item_repository.upsert_many(updated_news_items)

    # Update information in feed item with latest information from the url.
    feed.last_fetched = datetime.utcnow()
    feed.description = updated_feed.description
    feed.title = updated_feed.title
    feed.number_of_items = feed.number_of_items + len(new_feed_items)
    await repositories().feed_repository.upsert(feed)
    return update_result


def news_items_from_feed_items(feed_items: List[FeedItem], feed: Feed, user: User) -> List[NewsItem]:
    return [news_item_from_feed_item(feed_item, feed, user) for feed_item in feed_items]


domain_to_favicon_map = {
    r"^.*.sikkom.nl": "/favicons/sikkom.png",
    r"^.*.gic.nl": "/favicons/groningen-internet-courant.png",
    r"^.*.rtvnoord.nl": "/favicons/rtv-noord.ico",
    r"^.*.filtergroningen.nl": "https://i1.wp.com/www.filtergroningen.nl/wp-content/uploads/2017/03/favicon.png?fit=32%2C32&#038;ssl=1",
    r"^.*.tivolivredenburg.nl": "/favicons/tivoli.ico",
    r"^.*.vera-groningen.nl": "/favicons/vera.png",
    r"^.*.desmaakvanstad.nl": "/favicons/smaak-stad.jpg",
    r"^.*.focusgroningen.nl": "/favicons/focus-groningen.png",
    r"campus.groningen.nl": "/favicons/campus-groningen.png",
    r"^.*.paradiso.nl": "/favicons/paradiso.png",
    r"^.*.waag.org": "/favicons/waag.ico",
    r"^.*.simplon.nl": "/favicons/simplon.png",
    r"^.*.nu.nl": "/favicons/nu_logo.svg",
    r".*manjaro.org": "/favicons/manjaro.png",
    r"gemeente.groningen.nl": "/favicons/gemeente-groningen.png",
    r"thequietus.com": "/favicons/the-quietus.ico",
    r"^.*.slashdot.org": "/favicons/slashdot.ico",
    r"^.*pitchfork.com": "/favicons/pitchfork.png",
    r"^.*.oogtv.nl": "/favicons/oog-tv.png",
    r"^.*.matrix.org": "/favicons/matrix-logo.svg",
    r"^.*.arstechica.com": "/favicons/arstechnica.ico",
    r"^.*.jetbrains.png": "/favicons/jetbrains.png",
    r"^.*.melkweg.nl": "/favicons/melkweg.ico",
    r"^.*.013.nl": "/favicons/013.ico",
    r"^.*.spotgroningen.nl": "/favicons/spot-groningen.ico",
}


def determine_favicon_link(feed_item: FeedItem) -> str:
    feed_item_link_domain = urlparse(feed_item.link).netloc
    for regex, favicon in domain_to_favicon_map.items():
        if re.match(regex, feed_item_link_domain):
            return favicon
    return "/favicon.ico"


def news_item_from_feed_item(feed_item: FeedItem, feed: Feed, user: User) -> NewsItem:
    return NewsItem(
        feed_id=feed_item.feed_id,
        user_id=user.user_id,
        feed_item_id=feed_item.feed_item_id,
        feed_title=feed.title,
        title=feed_item.title,
        description=feed_item.description,
        link=feed_item.link,
        published=feed_item.published or now_in_utc(),
        favicon=determine_favicon_link(feed_item),
        created_on=now_in_utc(),
    )


async def upsert_gemeente_groningen_feed() -> Feed:
    feed = Feed(
        url="https://gemeente.groningen.nl/actueel/nieuws",
        title="Gemeente Groningen - algemeen nieuws",
        description="Algemeen nieuws van de gemeente.",
        feed_source_type=FeedSourceType.GEMEENTE_GRONINGEN,
        link="https://gemeente.groningen.nl/actueel/nieuws",
        image_url="https://gemeente.groningen.nl/sites/default/files/Logo-gemeente-Groningen---rood-zwart.png",
        image_link="https://gemeente.groningen.nl",
        image_title="Gemeente Groningen",
    )
    repo_feed = await repositories().feed_repository.find_by_url(feed.url)
    if repo_feed is None:
        repo_feed = await repositories().feed_repository.upsert(feed)
    return repo_feed
