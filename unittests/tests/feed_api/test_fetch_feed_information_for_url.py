from random import randint, choice
from typing import Tuple, List
from unittest.mock import MagicMock, patch, Mock, AsyncMock
from xml.etree.ElementTree import parse

import pytest
from aiohttp import ClientResponse, ClientSession
from faker import Faker

from api.feed_api import fetch_feed_information_for_url
from core_lib.application_data import Repositories
from core_lib.repositories import Feed, User, FeedItem
from tests.conftest import authorization_for


@pytest.mark.asyncio
@patch("api.feed_api.security")
async def test_unsubscribed(security_mock: Mock, faker: Faker, repositories: Repositories, user: User, feed: Feed):
    response_mock = MagicMock()
    repositories.feed_repository.find_by_url.return_value = feed

    with authorization_for(security_mock, user):
        response = await fetch_feed_information_for_url(
            response=response_mock, url=faker.url(), authorization=faker.sentence()
        )

        assert response.feed.feed_id == feed.feed_id
        assert not response.user_is_subscribed
        assert response_mock.status_code == 200


@pytest.mark.asyncio
@patch("api.feed_api.security")
async def test_subscribed(
    security_mock: Mock, faker: Faker, repositories: Repositories, subscribed_user: Tuple[User, Feed]
):
    response_mock = MagicMock()
    repositories.feed_repository.find_by_url.return_value = subscribed_user[1]

    with authorization_for(security_mock, subscribed_user[0]):
        response = await fetch_feed_information_for_url(
            response=response_mock, url=faker.url(), authorization=faker.sentence()
        )
        assert response.user_is_subscribed
        assert response_mock.status_code == 200


@pytest.mark.asyncio
@patch("api.feed_api.security")
async def test_parse_sample_feeds(security_mock: Mock, faker: Faker, repositories: Repositories, user: User):
    response_mock = MagicMock()
    repositories.feed_repository.find_by_url.return_value = None

    xml_test_files = [
        "tests/sample_rss_feeds/venues.xml",
        "tests/sample_rss_feeds/ars_technica.xml",
        "tests/sample_rss_feeds/pitchfork_best.xml",
    ]
    repositories.mock_client_session_for_files(xml_test_files)
    test_url = faker.url()

    for xml_test_file in xml_test_files:
        repositories.reset_mocks()
        repositories.mock_feed_repository().find_by_url.return_value = None
        with authorization_for(security_mock, user):
            response = await fetch_feed_information_for_url(response=response_mock, url=test_url, authorization="test")
            assert not response.user_is_subscribed
            assert response_mock.status_code == 201
            assert response.feed.feed_id is not None

            xml_element = parse(xml_test_file)
            assert response.feed.description == xml_element.find("channel/description").text
            assert response.feed.title == xml_element.find("channel/title").text
            assert response.feed.link == xml_element.find("channel/link").text
            assert response.feed.url == test_url.rstrip("/")
            if xml_element.find("channel/image") is not None:
                assert response.feed.image_url == xml_element.find("channel/image/url").text
                assert response.feed.image_link == xml_element.find("channel/image/link").text
                assert response.feed.image_title == xml_element.find("channel/image/title").text

        called_with = repositories.mock_feed_item_repository().upsert_many.call_args

        # Items should be uploaded and the feed itself should be uploaded
        repositories.mock_feed_repository().upsert.assert_called()
        repositories.mock_feed_item_repository().upsert_many.assert_called()


@pytest.mark.asyncio
@patch("api.feed_api.security")
async def test_unknown_feed_with_html(security_mock: Mock, faker: Faker, user: User, repositories: Repositories):

    repositories.mock_feed_repository().find_by_url.return_value = None
    html_file = "tests/sample_rss_feeds/pitchfork_best.html"
    xml_file = "tests/sample_rss_feeds/pitchfork_best.xml"
    repositories.mock_client_session_for_files([html_file, xml_file])
    response_mock = MagicMock()
    url = faker.url()

    with authorization_for(security_mock, user):
        response = await fetch_feed_information_for_url(response=response_mock, url=url, authorization=faker.word())
        assert response_mock.status_code == 201
        xml_element = parse(xml_file)

        assert response.feed is not None
        # Url used from the link in the html file.
        assert response.feed.url == "https://pitchfork.com/rss/reviews/best/albums"
        assert response.feed.description == xml_element.find("channel/description").text
        assert response.feed.title == xml_element.find("channel/title").text
        assert response.feed.link == xml_element.find("channel/link").text

        # Items should be uploaded and the feed itself should be uploaded
        repositories.mock_feed_repository().upsert.assert_called()
        repositories.mock_feed_item_repository().upsert_many.assert_called()


@pytest.mark.asyncio
@patch("api.feed_api.security")
async def test_parse_sample_feed_items(security_mock: Mock, faker: Faker, repositories: Repositories, user: User):
    response_mock = MagicMock()
    repositories.feed_repository.find_by_url.return_value = None

    xml_test_files = [
        "tests/sample_rss_feeds/venues.xml",
        "tests/sample_rss_feeds/ars_technica.xml",
        "tests/sample_rss_feeds/pitchfork_best.xml",
    ]
    repositories.mock_client_session_for_files(xml_test_files)
    test_url = faker.url()

    repositories.mock_feed_repository().find_by_url.return_value = None
    for xml_test_file in xml_test_files:
        with authorization_for(security_mock, user):
            response = await fetch_feed_information_for_url(response=response_mock, url=test_url, authorization="test")
            assert response_mock.status_code == 201
            assert response is not None

        called_with = repositories.mock_feed_item_repository().upsert_many.call_args
        upserted_items = called_with[0][0]
        xml_element = parse(xml_test_file)
        assert len(upserted_items) == len(xml_element.findall("channel/item"))

        item: FeedItem = choice(upserted_items)
        xml_item = [element for element in xml_element.findall("channel/item") if element.findtext("link") == item.link]

        assert len(xml_item) == 1
        assert item.title == xml_item[0].findtext("title")
        if xml_item[0].findtext("pubDate") is None:
            assert item.published is None
        else:
            assert item.published is not None
        assert item.created_on is not None
        assert item.description == xml_item[0].findtext("description")
