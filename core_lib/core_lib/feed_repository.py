from typing import Optional, List

from google.cloud import datastore
from google.cloud.datastore import Client

from core_lib.feed import Feed


class FeedRepository:
    def __init__(self, client: Client):
        self.client = client

    def find_by_url(self, url: str) -> Optional[Feed]:
        """ Find the Feed entity for the url. """
        query = self.client.query(kind="Feed")
        query.add_filter("url", "=", url)
        result = list(query.fetch())
        if not result:
            return None
        return Feed.parse_obj(result[0])

    def upsert_feed(self, feed: Feed) -> Feed:
        """ Upsert a feed into the repository. """
        entity = datastore.Entity(self.client.key("Feed", feed.feed_id))
        entity.update(feed.dict())
        self.client.put(entity)
        return Feed.parse_obj(entity)

    def all_feeds(self) -> List[Feed]:
        """ Retrieve all the feeds in the system. """
        query = self.client.query(kind="Feed")
        return [Feed.parse_obj(result) for result in query.fetch()]
