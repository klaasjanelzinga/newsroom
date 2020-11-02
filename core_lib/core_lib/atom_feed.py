import asyncio
import logging
from datetime import datetime
from typing import List, Optional
from xml.etree.ElementTree import Element, fromstring

import dateparser
import pytz
from aiohttp import ClientSession

from core_lib.application_data import repositories
from core_lib.feed_utils import upsert_new_items_for_feed, update_users_unread_count_with_refresh_results
from core_lib.repositories import Feed, FeedItem, FeedSourceType, RefreshResult

log = logging.getLogger(__file__)


def is_atom_file(text: str) -> bool:
    return "http://www.w3.org/2005/Atom" in text


def atom_document_to_feed(atom_url: str, tree: Element) -> Feed:
    title = tree.findtext("{http://www.w3.org/2005/Atom}title")

    description = tree.findtext("{http://www.w3.org/2005/Atom}subtitle")
    category = tree.findtext("{http://www.w3.org/2005/Atom}category")
    link = tree.findtext("{http://www.w3.org/2005/Atom}link") or atom_url

    return Feed(
        url=atom_url,
        title=title,
        link=link,
        description=description,
        category=category,
        feed_source_type=FeedSourceType.ATOM.name,
    )


def _parse_optional_datetime(freely_formatted_datetime: Optional[str]) -> Optional[datetime]:
    if freely_formatted_datetime is None:
        return None
    in_this_tz = dateparser.parse(freely_formatted_datetime, languages=["en"])
    if in_this_tz is None:
        return None
    return in_this_tz.astimezone(tz=pytz.UTC)


def _parse_optional_link_for_href(element: Optional[Element]) -> Optional[str]:
    if element is None:
        return None
    return element.get("href")


def atom_document_to_feed_items(feed: Feed, tree: Element) -> List[FeedItem]:
    item_elements = tree.findall("{http://www.w3.org/2005/Atom}entry")
    return [
        FeedItem(
            feed_id=feed.feed_id,
            title=item_element.findtext("{http://www.w3.org/2005/Atom}title"),
            link=_parse_optional_link_for_href(item_element.find("{http://www.w3.org/2005/Atom}link")),
            description=item_element.findtext("{http://www.w3.org/2005/Atom}content") or "",
            last_seen=datetime.utcnow(),
            published=_parse_optional_datetime(item_element.findtext("{http://www.w3.org/2005/Atom}published")),
            created_on=datetime.utcnow(),
        )
        for item_element in item_elements
    ]


async def refresh_atom_feed(session: ClientSession, feed: Feed) -> RefreshResult:
    log.info("Refreshing feed %s", feed)
    async with session.get(feed.url) as xml_response:
        with repositories.client.transaction():
            atom_document = fromstring(await xml_response.text(encoding="utf-8"))
            feed_from_rss = atom_document_to_feed(feed.url, atom_document)
            feed_items_from_rss = atom_document_to_feed_items(feed, atom_document)

            return RefreshResult(
                feed=feed, number_of_items=upsert_new_items_for_feed(feed, feed_from_rss, feed_items_from_rss)
            )


async def refresh_atom_feeds() -> int:
    """ Refreshes all active feeds and returns the number of refreshed feeds. """
    client_session = repositories.client_session
    feeds = repositories.feed_repository.get_active_feeds()
    tasks = [
        refresh_atom_feed(client_session, feed) for feed in feeds if feed.feed_source_type == FeedSourceType.ATOM.name
    ]
    refresh_results: List[RefreshResult] = await asyncio.gather(*tasks)
    update_users_unread_count_with_refresh_results(refresh_results)
    return len(tasks)
