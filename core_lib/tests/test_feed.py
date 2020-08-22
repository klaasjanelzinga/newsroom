from typing import List
from unittest.mock import MagicMock, Mock, AsyncMock

import pytest
from aiohttp import ClientSession, ClientResponse
from defusedxml.ElementTree import parse

from core_lib.feed import fetch_feed_information_for


def aiohttp_client_session_for_file(file_names: List[str]) -> MagicMock:

    def _response_for_file(file_name: str) -> AsyncMock:
        with open(file_name) as f:
            file = f.read()
            text_response = AsyncMock(ClientResponse)
            text_response.text.return_value = file

            response = Mock()
            response.__aenter__ = AsyncMock(return_value=text_response)
            response.__aexit__ = AsyncMock(return_value=None)
            return response

    client_session = AsyncMock(ClientSession)
    client_session.get.side_effect = [_response_for_file(file_name) for file_name in file_names]
    return client_session


@pytest.mark.asyncio
async def test_fetch_information_for():
    xml_files = ["tests/sample_rss_feeds/venues.xml", "tests/sample_rss_feeds/ars_technica.xml", "tests/sample_rss_feeds/pitchfork_best.xml"]
    for xml_file in xml_files:
        url = "https://venues.n-kj.nl/events.xml"
        client_session = aiohttp_client_session_for_file([xml_file])
        feed = await fetch_feed_information_for(client_session, url)
        xml_element = parse(xml_file)
        assert feed is not None
        assert feed.description == xml_element.find("channel/description").text
        assert feed.title == xml_element.find("channel/title").text
        assert feed.link == xml_element.find("channel/link").text
        assert feed.url == url
        if xml_element.find("channel/image") is not None:
            assert feed.image_url == xml_element.find("channel/image/url").text
            assert feed.image_link == xml_element.find("channel/image/link").text
            assert feed.image_title == xml_element.find("channel/image/title").text


@pytest.mark.asyncio
async def test_fetch_information_for_with_html():
    html_file = "tests/sample_rss_feeds/pitchfork_best.html"
    xml_file = "tests/sample_rss_feeds/pitchfork_best.xml"
    url = "https://venues.n-kj.nl/events.xml"
    client_session = aiohttp_client_session_for_file([html_file, xml_file])
    feed = await fetch_feed_information_for(client_session, url)
    xml_element = parse(xml_file)
    assert feed is not None
    # Url used from the link in the html file.
    assert feed.url == "https://pitchfork.com/rss/reviews/best/albums/"
    assert feed.description == xml_element.find("channel/description").text
    assert feed.title == xml_element.find("channel/title").text
    assert feed.link == xml_element.find("channel/link").text
