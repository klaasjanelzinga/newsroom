import logging
from typing import List, Optional

from aiohttp import ClientSession
from google.api_core.exceptions import ClientError, GoogleAPIError
from lxml.etree import ElementBase, fromstring

from core_lib.application_data import repositories
from core_lib.atom_feed import _parse_optional_datetime
from core_lib.feed_utils import upsert_new_items_for_feed
from core_lib.repositories import Feed, FeedItem, FeedSourceType, RefreshResult
from core_lib.utils import now_in_utc, parse_description, sanitize_link

log = logging.getLogger(__file__)


def is_rdf_document(text: bytes) -> bool:
    return b"<rdf:RDF xmlns:rdf=" in text


def rdf_document_to_feed(rss_url: str, tree: ElementBase) -> Feed:
    # required rss channel items
    title = tree.findtext("{*}channel/{*}title")
    description = parse_description(tree.findtext("{*}channel/{*}description"))
    link = tree.findtext("{*}channel/{*}link")
    # optional rss channel items
    category = tree.find("{*}channel/{*}category")
    image_tag = tree.find("{*}channel/{*}image")
    image_url = (
        image_tag.get("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource") if image_tag is not None else None
    )

    return Feed(
        url=rss_url.rstrip("/"),
        title=title,
        description=description,
        link=link,
        feed_source_type=FeedSourceType.RDF.name,
        category=category.text if category is not None else None,
        image_url=image_url if image_url is not None else None,
        image_title=None,
        image_link=None,
    )


def rdf_document_to_feed_items(feed: Feed, tree: ElementBase) -> List[FeedItem]:
    """ Creates a list of FeedItem objects from a xml tree for the feed. """
    item_elements = tree.findall("{*}item")
    return [
        FeedItem(
            feed_id=feed.feed_id,
            title=item_element.findtext("{*}title"),
            link=sanitize_link(item_element.findtext("{*}link")),
            description=parse_description(item_element.findtext("{*}description")),
            last_seen=now_in_utc(),
            published=_parse_optional_datetime(item_element.findtext("{*}date")),
            created_on=now_in_utc(),
        )
        for item_element in item_elements
    ]


async def refresh_rdf_feed(session: ClientSession, feed: Feed) -> Optional[RefreshResult]:
    log.info("Refreshing rdf feed %s", feed)
    try:
        async with session.get(feed.url) as xml_response:
            with repositories.client.transaction():
                rdf_document = fromstring(await xml_response.read())
                feed_from_rss = rdf_document_to_feed(feed.url, rdf_document)
                feed_items_from_rss = rdf_document_to_feed_items(feed, rdf_document)
                number_of_items = upsert_new_items_for_feed(feed, feed_from_rss, feed_items_from_rss)

                return RefreshResult(feed=feed, number_of_items=number_of_items)
    except (ClientError, TimeoutError, GoogleAPIError):
        log.exception("Error while refreshing feed %s", feed)
        return None
