import logging

from aiohttp import ClientSession, ClientTimeout
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
import sentry_sdk
from starlette.middleware.cors import CORSMiddleware

import api
from api.feed_api import feed_router
from api.news_item_api import news_router
from api.saved_items_api import saved_news_router
from api.security import Security
from api.user_api import user_router
import core_lib
from core_lib.app_config import AppConfig
from core_lib.application_data import Repositories, repositories
from core_lib.feed_utils import upsert_gemeente_groningen_feed

logging.root.setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)

app = FastAPI()


origins = [
    "http://localhost:5000",
    "https://newsroom.n-kj.nl",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST", "GET", "DELETE"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(feed_router)
app.include_router(news_router)
app.include_router(saved_news_router)


@app.on_event("startup")
async def startup_event() -> None:
    # pylint: disable=E0110,W0212
    if AppConfig.sentry_dsn_api() is not None:
        sentry_sdk.init(AppConfig.sentry_dsn_api(), traces_sample_rate=1.0, environment=AppConfig.environment())
    timeout = ClientTimeout(total=290)
    client_session = ClientSession(timeout=timeout)
    core_lib.application_data._repositories = Repositories(
        AsyncIOMotorClient(AppConfig.mongodb_url()), AppConfig.mongo_db(), client_session
    )
    api.api_application_data._security = Security(user_repository=repositories().user_repository)
    await upsert_gemeente_groningen_feed()
