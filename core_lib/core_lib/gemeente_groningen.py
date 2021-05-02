from datetime import datetime
import re
from typing import List

from bs4 import BeautifulSoup, Tag

from core_lib.repositories import Feed, FeedItem, FeedSourceType, User
from core_lib.utils import now_in_utc


def _sanitize_text(text: str) -> str:
    return re.sub(r" {2,}", "", text).replace("\n", " ")


def _description(article_tag: Tag) -> str:
    return article_tag.find("div", {"class": "teaser-body"}).find("div", {"class": "field-type-text-with-summary"}).text


def _link(article_tag: Tag) -> str:
    raw_link = article_tag.find("div").find("h2").find("a")["href"]
    return f"https://gemeente.groningen.nl{raw_link}"


def _title(article_tag: Tag) -> str:
    return _sanitize_text(article_tag.find("div").find("h2").find("a").text)


def gemeente_groningen_parser(feed: Feed, html_source: str) -> List[FeedItem]:
    soup = BeautifulSoup(html_source, features="html.parser")
    articles = soup.find_all("article")
    return [
        FeedItem(
            feed_id=feed.feed_id,
            title=_title(article),
            description=_description(article),
            link=_link(article),
            last_seen=now_in_utc(),
            published=datetime.fromisoformat(article.find("time")["datetime"]),
            created_on=now_in_utc(),
        )
        for article in articles
    ]
