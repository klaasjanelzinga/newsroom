import logging

from google.cloud import datastore

from core_lib.feed_repository import FeedRepository
from core_lib.user import UserRepository

logging.basicConfig(level=logging.INFO)

DATASTORE_CLIENT = datastore.Client()

user_repository = UserRepository(DATASTORE_CLIENT)
feed_repository = FeedRepository(DATASTORE_CLIENT)
