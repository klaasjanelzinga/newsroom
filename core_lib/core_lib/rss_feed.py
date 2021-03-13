from datetime import datetime
import logging
import threading
from typing import List, Optional

from aiohttp import ClientError, ClientSession
from bs4 import BeautifulSoup
import dateparser
from google.api_core.exceptions import GoogleAPIError
from lxml.etree import ElementBase, fromstring
import pytz

from core_lib.application_data import repositories
from core_lib.feed_utils import upsert_new_items_for_feed
from core_lib.repositories import Feed, FeedItem, FeedSourceType, RefreshResult
from core_lib.utils import now_in_utc, parse_description, sanitize_link

log = logging.getLogger(__file__)


def is_rss_document(text: bytes) -> bool:
    return b"<rss" in text


def is_html_with_rss_ref(text: bytes) -> Optional[str]:
    if b"<!DOCTYPE html>" in text or b"<html" in text:
        soup = BeautifulSoup(text, "html.parser")
        rss_links = soup.find_all("link", type="application/rss+xml")
        if len(rss_links) == 1:
            return rss_links[0].get("href")
    return None


def rss_document_to_feed(rss_url: str, tree: ElementBase) -> Feed:
    # required rss channel items
    title = tree.findtext("channel/title")
    description = parse_description(tree.findtext("channel/description"))
    link = tree.findtext("channel/link")
    # optional rss channel items
    category = tree.find("channel/category")
    image_url = tree.find("channel/image/url")
    image_title = tree.find("channel/image/title")
    image_link = tree.find("channel/image/link")

    return Feed(
        url=rss_url.rstrip("/"),
        title=title,
        description=description,
        link=link,
        feed_source_type=FeedSourceType.RSS.name,
        category=category.text if category is not None else None,
        image_url=image_url.text if image_url is not None else None,
        image_title=image_title.text if image_title is not None else None,
        image_link=image_link.text if image_link is not None else None,
    )


LOCALE_LOCK = threading.Lock()


def _parse_optional_rss_datetime(freely_formatted_datetime: Optional[str]) -> Optional[datetime]:
    """ Sun, 19 May 2002 15:21:36 GMT parsing to datetime. """
    if freely_formatted_datetime is None:
        return None
    in_this_tz = dateparser.parse(freely_formatted_datetime, languages=["en"])
    if in_this_tz is None:
        return None
    return in_this_tz.astimezone(tz=pytz.UTC)


def rss_document_to_feed_items(feed: Feed, tree: ElementBase) -> List[FeedItem]:
    """ Creates a list of FeedItem objects from a xml tree for the feed. """
    item_elements = tree.findall("channel/item")
    return [
        FeedItem(
            feed_id=feed.feed_id,
            title=item_element.findtext("title"),
            link=sanitize_link(item_element.findtext("link")),
            description=parse_description(item_element.findtext("description")),
            last_seen=now_in_utc(),
            published=_parse_optional_rss_datetime(item_element.findtext("pubDate")),
            created_on=now_in_utc(),
        )
        for item_element in item_elements
    ]


async def refresh_rss_feed(session: ClientSession, feed: Feed) -> Optional[RefreshResult]:
    log.info("Refreshing rss feed %s", feed)
    try:
        async with session.get(feed.url) as xml_response:
            with repositories.client.transaction():
                rss_document = fromstring(await xml_response.read())
                feed_from_rss = rss_document_to_feed(feed.url, rss_document)
                feed_items_from_rss = rss_document_to_feed_items(feed, rss_document)
                number_of_items = upsert_new_items_for_feed(feed, feed_from_rss, feed_items_from_rss)

                return RefreshResult(feed=feed, number_of_items=number_of_items)
    except (ClientError, TimeoutError, GoogleAPIError):
        log.exception("Error while refreshing feed %s", feed)
        return None
