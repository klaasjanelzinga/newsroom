import logging
from datetime import datetime, timedelta
from typing import Optional
from xml.etree.ElementTree import Element

from aiohttp import ClientSession, ClientConnectorError
from defusedxml.ElementTree import fromstring

from core_lib.application_data import repositories
from core_lib.atom_feed import is_atom_file, atom_document_to_feed_items, atom_document_to_feed
from core_lib.feed_utils import news_items_from_feed_items
from core_lib.repositories import Feed, Subscription, User
from core_lib.rss_feed import rss_document_to_feed, rss_document_to_feed_items, is_rss_document, is_html_with_rss_ref

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
                rss_ref = is_html_with_rss_ref(text)
                if rss_ref is not None:
                    async with session.get(rss_ref) as xml_response:
                        return _process_rss_document(rss_ref, fromstring(await xml_response.text()))
                elif is_rss_document(text):
                    return _process_rss_document(url, fromstring(text))
                elif is_atom_file(text):
                    return _process_atom_document(url=url, atom_document=fromstring(text))
        return None
    except ClientConnectorError as cce:
        raise NetworkingException(f"Url {url} not reachable. Details: {cce.__str__()}") from cce


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


def delete_read_items() -> int:
    with repositories.client.transaction():
        feed_item_keys = repositories.feed_item_repository.fetch_all_last_seen_before(
            datetime.utcnow() - timedelta(days=3)
        )
        feed_item_keys = repositories.news_item_repository.filter_feed_item_keys_that_are_read(feed_item_keys)
        repositories.feed_item_repository.delete_keys(feed_item_keys)
        repositories.news_item_repository.delete_with_feed_item_keys(feed_item_keys)
    return len(feed_item_keys)


def update_number_items_in_feeds() -> None:
    for feed in repositories.feed_repository.all_feeds():
        feed.number_of_items = repositories.feed_item_repository.count_all_for_feed(feed)
        repositories.feed_repository.upsert(feed)
