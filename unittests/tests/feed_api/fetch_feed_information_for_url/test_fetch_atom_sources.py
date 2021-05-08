from random import choice
from unittest.mock import MagicMock

import pytest
from faker import Faker
from lxml.etree import parse

from api.feed_api import fetch_feed_information_for_url
from core_lib.application_data import Repositories
from core_lib.repositories import User, FeedItem
from tests.conftest import ClientSessionMocker


@pytest.mark.asyncio
async def test_atom_feed(
    faker: Faker, repositories: Repositories, client_session_mocker: ClientSessionMocker, user: User, user_bearer_token
):
    response_mock = MagicMock()

    xml_test_files = [
        "sample-files/atom/thequietus.xml",
    ]
    client_session_mocker.setup_client_session_for(xml_test_files)
    test_url = faker.url()

    response = await fetch_feed_information_for_url(
        response=response_mock, url=test_url, authorization=user_bearer_token
    )
    assert response_mock.status_code == 201
    assert response is not None

    assert response.feed.feed_id is not None
    assert response.feed.description is None
    assert response.feed.title == "The Quietus | All Articles"

    xml_element = parse(xml_test_files[0])
    assert await repositories.feed_item_repository.count({}) == len(
        xml_element.findall("{http://www.w3.org/2005/Atom}entry")
    )

    item: FeedItem = choice(await repositories.feed_item_repository.fetch_all_for_feed(response.feed))
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
