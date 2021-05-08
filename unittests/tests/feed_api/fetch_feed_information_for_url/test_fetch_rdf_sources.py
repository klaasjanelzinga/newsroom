from random import choice
from unittest.mock import MagicMock

import pytest
from faker import Faker
from lxml.etree import parse

from api.feed_api import fetch_feed_information_for_url
from core_lib.application_data import Repositories
from core_lib.repositories import User, FeedItem
from core_lib.utils import sanitize_link
from tests.conftest import ClientSessionMocker, clean_data_repositories


@pytest.mark.asyncio
async def test_unknown_rdf_feed_with_html(
    faker: Faker,
    user: User,
    repositories: Repositories,
    client_session_mocker: ClientSessionMocker,
    user_bearer_token: str,
):

    html_file = "sample-files/rdf_sources/slashdot.html"
    xml_file = "sample-files/rdf_sources/slashdot.xml"
    client_session_mocker.setup_client_session_for([html_file, xml_file])
    response_mock = MagicMock()
    url = faker.url()

    response = await fetch_feed_information_for_url(response=response_mock, url=url, authorization=user_bearer_token)
    assert response.feed.link == "https://slashdot.org/"
    assert response.feed.number_of_items == 15
    assert response.feed.description == "News for nerds, stuff that matters"
    assert response.feed.title == "Slashdot"
    assert await repositories.feed_item_repository.count({}) == 15
    assert await repositories.feed_repository.count({}) == 1


@pytest.mark.asyncio
async def test_parse_sample_rdf_feeds(
    repositories: Repositories, client_session_mocker: ClientSessionMocker, faker: Faker, user: User, user_bearer_token
):
    response_mock = MagicMock()

    xml_test_files = [
        "sample-files/rdf_sources/slashdot.xml",
    ]
    client_session_mocker.setup_client_session_for(xml_test_files)
    test_url = faker.url()

    for xml_test_file in xml_test_files:
        clean_data_repositories(repositories)
        response = await fetch_feed_information_for_url(
            response=response_mock, url=test_url, authorization=user_bearer_token
        )

        assert not response.user_is_subscribed
        assert response_mock.status_code == 201
        assert response.feed is not None
        assert response.feed.feed_id is not None
        xml_element = parse(xml_test_file)
        assert response.feed.description == xml_element.find("{*}channel/{*}description").text
        assert response.feed.title == xml_element.find("{*}channel/{*}title").text
        assert response.feed.link == xml_element.find("{*}channel/{*}link").text
        assert response.feed.url == test_url.rstrip("/")
        assert response.feed.image_url == "https://a.fsdn.com/sd/topics/topicslashdot.gif"
        assert response.feed.image_link is None
        assert response.feed.image_title is None
        assert await repositories.feed_repository.count({}) == 1
        item: FeedItem = choice(await repositories.feed_item_repository.fetch_all_for_feed(response.feed))
        xml_item = [
            element
            for element in xml_element.findall("{*}item")
            if sanitize_link(element.findtext("{*}link")) == item.link
        ]

        assert len(xml_item) == 1
        assert xml_item[0].findtext("{*}title") in item.title
        if xml_item[0].findtext("{*}date") is None:
            assert item.published is None
        else:
            assert item.published is not None
        assert item.created_on is not None
        assert item.description == xml_item[0].findtext("{*}description")[:1400]
