import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, List
from xml.etree.ElementTree import Element

from aiohttp import ClientSession, ClientConnectorError
from bs4 import BeautifulSoup
from defusedxml.ElementTree import fromstring

from core_lib.application_data import repositories
from core_lib.atom import is_atom_file, atom_document_to_feed_items, atom_document_to_feed
from core_lib.repositories import Feed, Subscription, NewsItem, User, FeedItem
from core_lib.rss import rss_document_to_feed, rss_document_to_feed_items


log = logging.getLogger(__file__)


def _process_rss_document(
    url: str,
    rss_document: Element,
) -> Feed:
    feed = rss_document_to_feed(url, rss_document)
    feed_items = rss_document_to_feed_items(feed, rss_document)
    feed.number_of_items = len(feed_items)
    feed = repositories.feed_repository.upsert(feed)
    repositories.feed_item_repository.upsert_many(feed_items)
    return feed


def _process_atom_document(url: str, atom_document: Element) -> Feed:
    feed = atom_document_to_feed(url, atom_document)
    feed_items = atom_document_to_feed_items(feed, atom_document)
    feed.number_of_items = len(feed_items)
    feed = repositories.feed_repository.upsert(feed)
    repositories.feed_item_repository.upsert_many(feed_items)
    return feed


class NetworkingException(Exception):
    pass


async def fetch_feed_information_for(
    session: ClientSession,
    url: str,
) -> Optional[Feed]:
    """
    If the fetched data from url is not an xml document, parse for link for the application/rss+xml type.
    In this href attribute there will be an xml-location.

    <link rel="alternate" type="application/rss+xml" title="RSS" href="https://pitchfork.com/rss/reviews/best/albums/"/>

    :param session: Client session for the http asyncio client.
    :param url: The url to fetch information from. Maybe an html document containing the link or an rss-xml document.
    :return: A feed object or None if no feed found.
    """
    try:
        async with session.get(url, headers={"accept-encoding": "gzip"}) as response:
            with repositories.client.transaction():
                text = await response.text(encoding="utf-8")
                if text.find("<!DOCTYPE html>") != -1 or text.find("<html") != -1:
                    soup = BeautifulSoup(text, "html.parser")
                    rss_links = soup.find_all("link", type="application/rss+xml")
                    if len(rss_links) == 1:
                        rss_url = rss_links[0].get("href")
                        async with session.get(rss_url) as xml_response:
                            rss_document = fromstring(await xml_response.text())
                            return _process_rss_document(rss_url, rss_document)
                elif text.find("<rss") != -1:
                    rss_document = fromstring(text)
                    return _process_rss_document(url, rss_document)
                elif is_atom_file(text):
                    atom_document = fromstring(text)
                    return _process_atom_document(url=url, atom_document=atom_document)
        return None
    except ClientConnectorError as cce:
        raise NetworkingException(f"Url {url} not reachable. Details: {cce.__str__()}") from cce


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


def news_items_from_feed_items(feed_items: List[FeedItem], feed: Feed, user: User) -> List[NewsItem]:
    return [news_item_from_feed_item(feed_item, feed, user) for feed_item in feed_items]


def subscribe_user_to_feed(
    user: User,
    feed: Feed,
) -> User:
    with repositories.client.transaction():
        if feed.feed_id not in user.subscribed_to:
            user.subscribed_to.append(feed.feed_id)
            subscription = Subscription(feed_id=feed.feed_id, user_id=user.user_id)
            feed.number_of_subscriptions = feed.number_of_subscriptions + 1
            feed_items = repositories.feed_item_repository.fetch_all_for_feed(feed)
            news_items = news_items_from_feed_items(feed_items, feed, user)

            repositories.subscription_repository.upsert(subscription)
            repositories.user_repository.upsert(user)
            repositories.feed_repository.upsert(feed)
            repositories.news_item_repository.upsert_many(news_items)
    return user


def unsubscribe_user_from_feed(user: User, feed: Feed) -> User:
    with repositories.client.transaction():
        if feed.feed_id in user.subscribed_to:
            user.subscribed_to.remove(feed.feed_id)

            repositories.news_item_repository.delete_user_feed(user=user, feed=feed)
            repositories.subscription_repository.delete_user_feed(user=user, feed=feed)
            feed.number_of_subscriptions = feed.number_of_subscriptions - 1

            repositories.feed_repository.upsert(feed)
            repositories.user_repository.upsert(user)
    return user


async def refresh_rss_feed(session: ClientSession, feed: Feed) -> Feed:
    log.info("Refreshing feed %s", feed)
    async with session.get(feed.url) as xml_response:
        with repositories.client.transaction():
            rss_document = fromstring(await xml_response.text())
            feed_from_rss = rss_document_to_feed(feed.url, rss_document)
            feed_items_from_rss = rss_document_to_feed_items(feed, rss_document)

            # Upload new feed_items
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
            feed.description = feed_from_rss.description
            feed.title = feed_from_rss.title
            feed.number_of_items = feed.number_of_items + len(new_feed_items)

            repositories.feed_repository.upsert(feed)
            return feed


async def refresh_rss_feeds() -> int:
    """ Refreshes all active feeds and returns the number of refreshed feeds. """
    client_session = repositories.client_session
    feeds = repositories.feed_repository.get_active_feeds()
    tasks = [refresh_rss_feed(client_session, feed) for feed in feeds]
    await asyncio.gather(*tasks)
    return len(feeds)


async def delete_read_items() -> int:
    with repositories.client.transaction():
        feed_item_keys = repositories.feed_item_repository.fetch_all_last_seen_before(
            datetime.utcnow() - timedelta(days=3)
        )
        feed_item_keys = repositories.news_item_repository.filter_feed_item_keys_that_are_read(feed_item_keys)
        repositories.feed_item_repository.delete_keys(feed_item_keys)
        repositories.news_item_repository.delete_with_feed_item_keys(feed_item_keys)
    return len(feed_item_keys)
