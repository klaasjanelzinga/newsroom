import asyncio
from datetime import datetime, timedelta
import logging
from typing import List, Optional

from aiohttp import ClientConnectorError, ClientSession
from lxml.etree import fromstring
from pymongo import ReadPreference, WriteConcern
from pymongo.read_concern import ReadConcern

from core_lib.application_data import repositories
from core_lib.atom_feed import atom_document_to_feed, atom_document_to_feed_items, is_atom_file, refresh_atom_feed
from core_lib.feed_utils import news_items_from_feed_items, upsert_new_feed_items_for_feed
from core_lib.html_feed import refresh_html_feed
from core_lib.rdf_feed import is_rdf_document, rdf_document_to_feed, rdf_document_to_feed_items, refresh_rdf_feed
from core_lib.repositories import Feed, FeedItem, FeedSourceType, Subscription, User
from core_lib.rss_feed import (
    is_html_with_rss_ref,
    is_rss_document,
    refresh_rss_feed,
    rss_document_to_feed,
    rss_document_to_feed_items,
)

log = logging.getLogger(__file__)


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
        feed: Optional[Feed] = None
        feed_items: List[FeedItem] = []
        async with session.get(url, headers={"accept-encoding": "gzip"}) as response:
            text = await response.read()
            rss_ref = is_html_with_rss_ref(text)
            if rss_ref is not None:
                async with session.get(rss_ref) as xml_response:
                    text = await xml_response.read()

            if is_rss_document(text):
                rss_document = fromstring(text)
                feed = rss_document_to_feed(rss_ref if rss_ref is not None else url, rss_document)
                feed_items = rss_document_to_feed_items(feed, rss_document)
            elif is_rdf_document(text):
                rdf_document = fromstring(text)
                feed = rdf_document_to_feed(url, rdf_document)
                feed_items = rdf_document_to_feed_items(feed, rdf_document)
            elif is_atom_file(text):
                atom_document = fromstring(text)
                feed = atom_document_to_feed(url, atom_document)
                feed_items = atom_document_to_feed_items(feed, atom_document)
        if feed is not None:
            feed.number_of_items = await upsert_new_feed_items_for_feed(feed, feed_items)
            feed = await repositories.feed_repository.upsert(feed)
        return feed
    except ClientConnectorError as cce:
        raise NetworkingException(f"Url {url} not reachable. Details: {cce.__str__()}") from cce


async def subscribe_user_to_feed(
    user: User,
    feed: Feed,
) -> User:

    async with await repositories.client.start_session() as session:
        async with session.start_transaction():
            user.subscribed_to.append(feed.feed_id)
            feed.number_of_subscriptions = feed.number_of_subscriptions + 1
            feed_items = await repositories.feed_item_repository.fetch_all_for_feed(feed)
            news_items = news_items_from_feed_items(feed_items, feed, user)
            user.number_of_unread_items += len(news_items)

            await repositories.user_repository.upsert(user)
            await repositories.feed_repository.upsert(feed)
            await repositories.news_item_repository.upsert_many(news_items)
    return user


async def unsubscribe_user_from_feed(user: User, feed: Feed) -> User:
    async with await repositories.client.start_session() as session:
        async with session.start_transaction():
            if feed.feed_id in user.subscribed_to:
                user.subscribed_to.remove(feed.feed_id)

                news_items_deleted = await repositories.news_item_repository.delete_user_feed(user=user, feed=feed)
                feed.number_of_subscriptions = max(0, feed.number_of_subscriptions - 1)
                user.number_of_unread_items = max(0, user.number_of_unread_items - news_items_deleted)

                await repositories.feed_repository.upsert(feed)
                await repositories.user_repository.upsert(user)
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


async def refresh_all_feeds(include_fixed_feeds: bool = True) -> int:
    """Refreshes all active feeds and returns the number of refreshed feeds."""
    client_session = repositories.client_session
    feeds = repositories.feed_repository.get_active_feeds()
    tasks = [
        refresh_rss_feed(client_session, feed) for feed in feeds if feed.feed_source_type == FeedSourceType.RSS.name
    ]
    tasks.extend(
        [refresh_atom_feed(client_session, feed) for feed in feeds if feed.feed_source_type == FeedSourceType.ATOM.name]
    )
    tasks.extend(
        [refresh_rdf_feed(client_session, feed) for feed in feeds if feed.feed_source_type == FeedSourceType.RDF.name]
    )
    tasks.extend(
        [
            refresh_html_feed(client_session, feed)
            for feed in feeds
            if feed.feed_source_type == FeedSourceType.GEMEENTE_GRONINGEN.name
        ]
    )

    await asyncio.gather(*tasks)
    return len(tasks)
