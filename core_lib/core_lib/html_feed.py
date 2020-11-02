import asyncio
import logging

from aiohttp import ClientSession

from core_lib.application_data import repositories, html_feeds, html_feed_parsers
from core_lib.repositories import Feed, RefreshResult
from core_lib.feed_utils import upsert_new_items_for_feed, update_users_unread_count_with_refresh_results

log = logging.getLogger(__file__)


async def refresh_html_feed(session: ClientSession, feed: Feed) -> RefreshResult:
    log.info("Refreshing %s", feed)
    async with session.get(feed.url) as html:
        with repositories.client.transaction():
            parser = html_feed_parsers[feed.feed_id]
            feed_items = parser(feed, await html.text(encoding="utf-8"))
            number_of_new_items = upsert_new_items_for_feed(feed, feed, feed_items)
    return RefreshResult(feed=feed, number_of_items=number_of_new_items)


async def refresh_html_feeds() -> int:
    client_session = repositories.client_session
    tasks = [refresh_html_feed(client_session, html_feed) for html_feed in html_feeds]
    refresh_results = await asyncio.gather(*tasks)
    update_users_unread_count_with_refresh_results(refresh_results)
    return len(html_feeds)
