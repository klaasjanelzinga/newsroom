import logging

from aiohttp import ClientSession, ClientTimeout
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
import sentry_sdk

import core_lib
from core_lib.app_config import AppConfig
from core_lib.application_data import Repositories
from cron.maintenance_api import maintenance_router

logging.root.setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(maintenance_router)


@app.on_event("startup")
async def startup_event() -> None:
    # pylint: disable=E0110,W0212
    if AppConfig.sentry_dsn_cron() is not None:
        sentry_sdk.init(AppConfig.sentry_dsn_cron(), traces_sample_rate=1.0)
    timeout = ClientTimeout(total=290)
    client_session = ClientSession(timeout=timeout)
    core_lib.application_data._repositories = Repositories(
        AsyncIOMotorClient(AppConfig.mongodb_url()), AppConfig.mongo_db(), client_session
    )
