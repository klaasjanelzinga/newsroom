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
            if feed.feed_source_type == FeedSourceType.GEMEENTE_GRONINGEN:
                feed_items = gemeente_groningen_parser(feed, await html.text(encoding="utf-8"))
                async with await repositories.client.start_session() as mongo_session:
                    async with mongo_session.start_transaction():
                        number_of_items = await upsert_new_items_for_feed(feed, feed, feed_items)
                return RefreshResult(feed=feed, number_of_items=number_of_items)

            raise Exception(f"No support for feed source type in feed {feed}")
    except (ClientError, TimeoutError):
        log.exception("Error while refreshing feed %s", feed)
        return None
