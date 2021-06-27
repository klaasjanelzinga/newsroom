import logging

from aiohttp import ClientError, ClientSession

from core_lib.application_data import repositories
from core_lib.feed_utils import UpdateResult, upsert_new_items_for_feed
from core_lib.gemeente_groningen import gemeente_groningen_parser
from core_lib.repositories import Feed, FeedSourceType

log = logging.getLogger(__file__)


async def refresh_html_feed(session: ClientSession, feed: Feed) -> UpdateResult:
    log.info("Refreshing %s", feed)
    try:
        async with session.get(feed.url) as html:
            if feed.feed_source_type == FeedSourceType.GEMEENTE_GRONINGEN:
                feed_items = gemeente_groningen_parser(feed, await html.text(encoding="utf-8"))
                async with await repositories().mongo_client.start_session() as mongo_session:
                    async with mongo_session.start_transaction():
                        update_result = await upsert_new_items_for_feed(feed, feed, feed_items)
                return update_result

            raise Exception(f"No support for feed source type in feed {feed}")
    except (ClientError, TimeoutError):
        log.exception("Error while refreshing feed %s", feed)
        return UpdateResult()
