import logging

from google.cloud import datastore

from core_lib.repositories import (
    FeedRepository,
    SubscriptionRepository,
    FeedItemRepository,
    NewsItemRepository,
    UserRepository,
)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__file__)


DATASTORE_CLIENT = datastore.Client()


user_repository: UserRepository = UserRepository(DATASTORE_CLIENT)
feed_repository: FeedRepository = FeedRepository(DATASTORE_CLIENT)
feed_item_repository: FeedItemRepository = FeedItemRepository(DATASTORE_CLIENT)
subscription_repository: SubscriptionRepository = SubscriptionRepository(DATASTORE_CLIENT)
news_item_repository: NewsItemRepository = NewsItemRepository(DATASTORE_CLIENT)
