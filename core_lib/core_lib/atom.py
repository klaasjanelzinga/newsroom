from datetime import datetime
from typing import List, Optional
from xml.etree.ElementTree import Element

import dateparser
import pytz

from core_lib.repositories import Feed, FeedItem


def is_atom_file(text: str) -> bool:
    return "http://www.w3.org/2005/Atom" in text


def atom_document_to_feed(atom_url: str, tree: Element) -> Feed:
    title = tree.findtext("{http://www.w3.org/2005/Atom}title")

    description = tree.findtext("{http://www.w3.org/2005/Atom}subtitle")
    category = tree.findtext("{http://www.w3.org/2005/Atom}category")
    link = tree.findtext("{http://www.w3.org/2005/Atom}link") or atom_url

    return Feed(url=atom_url, title=title, link=link, description=description, category=category)


def _parse_optional_datetime(freely_formatted_datetime: Optional[str]) -> Optional[datetime]:
    if freely_formatted_datetime is None:
        return None
    in_this_tz: datetime = dateparser.parse(freely_formatted_datetime, languages=["en"])
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
