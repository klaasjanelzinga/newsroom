from typing import Optional
from xml.etree.ElementTree import Element

from aiohttp import ClientSession, ClientConnectorError
from bs4 import BeautifulSoup
from defusedxml.ElementTree import fromstring

from core_lib.application_data import (
    feed_item_repository,
    feed_repository,
    DATASTORE_CLIENT,
    subscription_repository,
    user_repository,
    news_item_repository,
)
from core_lib.repositories import Feed, Subscription, NewsItem, User
from core_lib.rss import rss_document_to_feed, rss_document_to_feed_items


def _process_rss_document(
    url: str,
    rss_document: Element,
) -> Feed:
    feed = rss_document_to_feed(url, rss_document)
    feed_items = rss_document_to_feed_items(feed, rss_document)
    feed.number_of_items = len(feed_items)
    feed = feed_repository.upsert(feed)
    feed_item_repository.upsert_many(feed_items)
    return feed


class NetworkingException(Exception):
    pass


async def fetch_feed_information_for(
    session: ClientSession,
    url: str,
) -> Optional[Feed]:
    """
    If the fetched data from url is not an xml document, parse for link for the application/rss+xml type.
    In this href attribute there will be an xml-location.

    <link rel="alternate" type="application/rss+xml" title="RSS" href="https://pitchfork.com/rss/reviews/best/albums/"/>

    :param session: Client session for the http asyncio client.
    :param url: The url to fetch information from. Maybe an html document containing the link or an rss-xml document.
    :return: A feed object or None if no feed found.
    """
    try:
        async with session.get(url) as response:
            with DATASTORE_CLIENT.transaction():
                text = await response.text()
                if text.find("<!DOCTYPE html>") != -1 or text.find("<html") != -1:
                    soup = BeautifulSoup(text, "html.parser")
                    rss_links = soup.find_all("link", type="application/rss+xml")
                    if len(rss_links) == 1:
                        rss_url = rss_links[0].get("href")
                        async with session.get(rss_url) as xml_response:
                            rss_document = fromstring(await xml_response.text())
                            return _process_rss_document(url, rss_document)
                elif text.find("<rss") != -1:
                    rss_document = fromstring(text)
                    return _process_rss_document(url, rss_document)
        return None
    except ClientConnectorError as cce:
        raise NetworkingException(f"Url {url} not reachable. Details: {cce.__str__()}")


def subscribe_user_to_feed(
    user: User,
    feed: Feed,
) -> User:
    with DATASTORE_CLIENT.transaction():
        if feed.feed_id not in user.subscribed_to:
            user.subscribed_to.append(feed.feed_id)
            subscription = Subscription(feed_id=feed.feed_id, user_id=user.email)
            feed.number_of_subscriptions = feed.number_of_subscriptions + 1
            feed_items = feed_item_repository.fetch_all_for_feed(feed)
            news_items = [
                NewsItem(
                    feed_id=feed.feed_id,
                    user_id=user.email,
                    feed_item_id=feed_item.feed_item_id,
                )
                for feed_item in feed_items
            ]

            subscription_repository.upsert(subscription)
            user_repository.upsert(user)
            feed_repository.upsert(feed)
            news_item_repository.upsert_many(news_items=news_items)
    return user


def unsubscribe_user_from_feed(user: User, feed: Feed) -> User:
    with DATASTORE_CLIENT.transaction():
        if feed.feed_id in user.subscribed_to:
            user.subscribed_to.remove(feed.feed_id)

            news_item_repository.delete_user_feed(user=user, feed=feed)
            subscription_repository.delete_user_feed(user=user, feed=feed)
            feed.number_of_subscriptions = feed.number_of_subscriptions - 1

            feed_repository.upsert(feed)
            user_repository.upsert(user)
    return user
