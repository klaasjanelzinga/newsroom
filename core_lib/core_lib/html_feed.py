import logging
from typing import Optional

from aiohttp import ClientError, ClientSession

from core_lib.application_data import repositories
from core_lib.feed_utils import upsert_new_items_for_feed
from core_lib.gemeente_groningen import gemeente_groningen_parser
from core_lib.repositories import Feed, RefreshResult, FeedSourceType

log = logging.getLogger(__file__)


async def refresh_html_feed(session: ClientSession, feed: Feed) -> Optional[RefreshResult]:
    log.info("Refreshing %s", feed)
    try:
        async with session.get(feed.url) as html:
            with repositories.client.transaction():
                if feed.feed_source_type == FeedSourceType.GEMEENTE_GRONINGEN:
                    feed_items = gemeente_groningen_parser(feed, await html.text(encoding="utf-8"))
                    number_of_new_items = upsert_new_items_for_feed(feed, feed, feed_items)
                else:
                    raise Exception(f"No support for feed source type in feed {feed}")
        return RefreshResult(feed=feed, number_of_items=number_of_new_items)
    except (ClientError, TimeoutError):
        log.exception("Error while refreshing feed %s", feed)
        return None
