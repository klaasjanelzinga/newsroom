import locale
import threading
from contextlib import contextmanager
from datetime import datetime
from typing import Generator, Optional, List
from xml.etree.ElementTree import Element

import dateparser
import pytz

from core_lib.repositories import Feed, FeedItem


def rss_document_to_feed(rss_url: str, tree: Element) -> Feed:
    # required rss channel items
    title = tree.findtext("channel/title")
    description = tree.findtext("channel/description")
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
        category=category.text if category is not None else None,
        image_url=image_url.text if image_url is not None else None,
        image_title=image_title.text if image_title is not None else None,
        image_link=image_link.text if image_link is not None else None,
    )


LOCALE_LOCK = threading.Lock()


@contextmanager
def setlocale(name: str) -> Generator:
    with LOCALE_LOCK:
        saved = locale.setlocale(locale.LC_ALL)
        try:
            yield locale.setlocale(locale.LC_ALL, name)
        finally:
            locale.setlocale(locale.LC_ALL, saved)


def _parse_optional_rss_datetime(freely_formatted_datetime: Optional[str]) -> Optional[datetime]:
    """ Sun, 19 May 2002 15:21:36 GMT parsing to datetime. """
    if freely_formatted_datetime is None:
        return None
    in_this_tz: datetime = dateparser.parse(freely_formatted_datetime, languages=["en"])
    return in_this_tz.astimezone(tz=pytz.UTC)


def rss_document_to_feed_items(feed: Feed, tree: Element) -> List[FeedItem]:
    item_elements = tree.findall("channel/item")
    return [
        FeedItem(
            feed_id=feed.feed_id,
            title=item_element.findtext("title"),
            link=item_element.findtext("link"),
            description=item_element.findtext("description"),
            published=_parse_optional_rss_datetime(item_element.findtext("pubDate")),
            created_on=datetime.utcnow(),
        )
        for item_element in item_elements
    ]
