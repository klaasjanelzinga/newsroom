import logging

from fastapi import FastAPI
import sentry_sdk
from starlette.middleware.cors import CORSMiddleware

from api.feed_api import feed_router
from api.news_item_api import news_router
from api.saved_items_api import saved_news_router
from api.user_api import user_router
from core_lib.app_config import AppConfig
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

if AppConfig.sentry_dsn_api() is not None:
    sentry_sdk.init(AppConfig.sentry_dsn_api(), traces_sample_rate=1.0, environment=AppConfig.environment())


@app.on_event("startup")
async def startup_event():
    await upsert_gemeente_groningen_feed()
