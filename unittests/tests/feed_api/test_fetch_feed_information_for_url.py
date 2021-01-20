from random import choice
from unittest.mock import MagicMock, patch, Mock

import pytest
from faker import Faker
from lxml.etree import parse

from api.feed_api import fetch_feed_information_for_url, FeedWithSubscriptionInformationResponse
from core_lib.feed import subscribe_user_to_feed
from core_lib.repositories import Feed, User, FeedItem
from tests.conftest import authorization_for
from tests.mock_repositories import MockRepositories


@pytest.mark.asyncio
@patch("api.feed_api.security")
async def test_unsubscribed(security_mock: Mock, faker: Faker, repositories: MockRepositories, user: User, feed: Feed):
    response_mock = MagicMock()

    with authorization_for(security_mock, user, repositories):
        response = await fetch_feed_information_for_url(
            response=response_mock, url=feed.url, authorization=faker.sentence()
        )

        assert response.feed.feed_id == feed.feed_id
        assert not response.user_is_subscribed
        assert response_mock.status_code == 200


@pytest.mark.asyncio
@patch("api.feed_api.security")
async def test_subscribed(security_mock: Mock, faker: Faker, repositories: MockRepositories, user: User, feed: Feed):
    response_mock = MagicMock()
    subscribe_user_to_feed(user, feed)

    with authorization_for(security_mock, user, repositories):
        response = await fetch_feed_information_for_url(
            response=response_mock, url=feed.url, authorization=faker.sentence()
        )
        assert response.user_is_subscribed
        assert response_mock.status_code == 200


def _assert_fetch_feed_information_response(
    response: FeedWithSubscriptionInformationResponse,
    response_mock: MagicMock,
    expected_url: str,
    xml_test_file: str,
    repositories: MockRepositories,
):
    assert not response.user_is_subscribed
    assert response_mock.status_code == 201
    assert response.feed is not None
    assert response.feed.feed_id is not None
    xml_element = parse(xml_test_file)
    assert response.feed.description == xml_element.find("channel/description").text
    assert response.feed.title == xml_element.find("channel/title").text
    assert response.feed.link == xml_element.find("channel/link").text
    assert response.feed.url == expected_url.rstrip("/")
    if xml_element.find("channel/image") is not None:
        assert response.feed.image_url == xml_element.find("channel/image/url").text
        assert response.feed.image_link == xml_element.find("channel/image/link").text
        assert response.feed.image_title == xml_element.find("channel/image/title").text
    assert repositories.feed_repository.count() == 1
    item: FeedItem = choice(repositories.feed_item_repository.fetch_all_for_feed(response.feed))
    xml_item = [element for element in xml_element.findall("channel/item") if element.findtext("link") == item.link]

    assert len(xml_item) == 1
    assert xml_item[0].findtext("title") in item.title  # Use of in since [Updated] may be prepended.
    if xml_item[0].findtext("pubDate") is None:
        assert item.published is None
    else:
        assert item.published is not None
    assert item.created_on is not None
    assert item.description == xml_item[0].findtext("description")[:1400]


@pytest.mark.asyncio
@patch("api.feed_api.security")
async def test_parse_sample_rss_feeds(security_mock: Mock, faker: Faker, repositories: MockRepositories, user: User):
    response_mock = MagicMock()

    xml_test_files = [
        "sample-files/rss_feeds/venues.xml",
        "sample-files/rss_feeds/ars_technica.xml",
        "sample-files/rss_feeds/pitchfork_best.xml",
    ]
    repositories.mock_client_session_for_files(xml_test_files)
    test_url = faker.url()

    for xml_test_file in xml_test_files:
        repositories.reset()
        with authorization_for(security_mock, user, repositories):
            response = await fetch_feed_information_for_url(response=response_mock, url=test_url, authorization="test")
            _assert_fetch_feed_information_response(
                response=response,
                response_mock=response_mock,
                expected_url=test_url,
                xml_test_file=xml_test_file,
                repositories=repositories,
            )


@pytest.mark.asyncio
@patch("api.feed_api.security")
async def test_unknown_feed_with_html(security_mock: Mock, faker: Faker, user: User, repositories: MockRepositories):

    html_file = "sample-files/rss_feeds/pitchfork_best.html"
    xml_file = "sample-files/rss_feeds/pitchfork_best.xml"
    repositories.mock_client_session_for_files([html_file, xml_file])
    response_mock = MagicMock()
    url = faker.url()

    with authorization_for(security_mock, user, repositories):
        response = await fetch_feed_information_for_url(response=response_mock, url=url, authorization=faker.word())
        _assert_fetch_feed_information_response(
            response=response,
            response_mock=response_mock,
            expected_url="https://pitchfork.com/rss/reviews/best/albums",
            xml_test_file=xml_file,
            repositories=repositories,
        )


@pytest.mark.asyncio
@patch("api.feed_api.security")
async def test_atom_feed(security_mock: Mock, faker: Faker, repositories: MockRepositories, user: User):
    response_mock = MagicMock()

    xml_test_files = [
        "sample-files/atom/thequietus.xml",
    ]
    repositories.mock_client_session_for_files(xml_test_files)
    test_url = faker.url()

    with authorization_for(security_mock, user, repositories):
        response = await fetch_feed_information_for_url(
            response=response_mock, url=test_url, authorization=faker.word()
        )
        assert response_mock.status_code == 201
        assert response is not None

        assert response.feed.feed_id is not None
        assert response.feed.description is None
        assert response.feed.title == "The Quietus | All Articles"

        xml_element = parse(xml_test_files[0])
        assert repositories.feed_item_repository.count() == len(
            xml_element.findall("{http://www.w3.org/2005/Atom}entry")
        )

        item: FeedItem = choice(repositories.feed_item_repository.fetch_all_for_feed(response.feed))
        xml_item = [
            element
            for element in xml_element.findall("{http://www.w3.org/2005/Atom}entry")
            if element.find("{http://www.w3.org/2005/Atom}link").get("href") == item.link
        ]
        assert len(xml_item) == 1
        assert item.title == xml_item[0].findtext("{http://www.w3.org/2005/Atom}title")
        if xml_item[0].findtext("{http://www.w3.org/2005/Atom}published") is None:
            assert item.published is None
        else:
            assert item.published is not None
        assert item.created_on is not None
        assert item.description == xml_item[0].findtext("{http://www.w3.org/2005/Atom}content")


@pytest.mark.asyncio
@patch("api.feed_api.security")
async def test_parse_edge_cases(security_mock: Mock, faker: Faker, repositories: MockRepositories, user: User):
    response_mock = MagicMock()

    xml_test_files = [
        "sample-files/rss_feeds/edge_case.xml",
    ]
    repositories.mock_client_session_for_files(xml_test_files)
    test_url = faker.url()

    with authorization_for(security_mock, user, repositories):
        response = await fetch_feed_information_for_url(response=response_mock, url=test_url, authorization="test")
        assert response_mock.status_code == 201
        assert response is not None

        assert response.feed.description is None
        assert repositories.feed_item_repository.count() == 1
        item: FeedItem = repositories.feed_item_repository.fetch_all_for_feed(response.feed)[0]
        assert item.description is None
