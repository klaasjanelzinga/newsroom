from datetime import datetime
from typing import Optional
from xml.etree.ElementTree import Element

from aiohttp import ClientSession
from bs4 import BeautifulSoup
from pydantic.main import BaseModel

from defusedxml.ElementTree import fromstring


class Feed(BaseModel):
    url: str
    title: str
    link: str
    description: str

    category: Optional[str]
    image_url: Optional[str]
    image_title: Optional[str]
    image_link: Optional[str]

    last_fetched: Optional[datetime]
    last_published: Optional[datetime]


def _parse_feed_information_from_rss_document(rss_url: str, tree: Element) -> Feed:
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
        url=rss_url,
        title=title,
        description=description,
        link=link,
        category=category.text if category is not None else None,
        image_url=image_url.text if image_url is not None else None,
        image_title=image_title.text if image_title is not None else None,
        image_link=image_link.text if image_link is not None else None,
    )


async def fetch_feed_information_for(session: ClientSession, url: str) -> Feed:
    """
    If the fetched data from url is not an xml document, parse for link with application/rss+xml type. In the href
    attribute there will be a xml-location.

    <link rel="alternate" type="application/rss+xml" title="RSS" href="https://pitchfork.com/rss/reviews/best/albums/"/>

    :param session: Client session for the http asyncio client.
    :param url: The url to fetch information from. Maybe an html document containing the link or an rss-xml document.
    :return: A feed object.
    """
    async with session.get(url) as response:
        text = await response.text()
        if text.find("<!DOCTYPE html>") != -1 or text.find("<html") != -1:
            soup = BeautifulSoup(text, "html.parser")
            rss_links = soup.find_all("link", type="application/rss+xml")
            if len(rss_links) == 1:
                rss_url = rss_links[0].get("href")
                async with session.get(rss_url) as xml_response:
                    return _parse_feed_information_from_rss_document(
                        rss_url, fromstring(await xml_response.text())
                    )
        elif text.find("<rss") != -1:
            return _parse_feed_information_from_rss_document(url, fromstring(text))
    raise ValueError("Document is neither html or rss")
