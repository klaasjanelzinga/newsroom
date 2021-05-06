import logging

from fastapi import FastAPI
import sentry_sdk

from core_lib.app_config import AppConfig
from cron.maintenance_api import maintenance_router

logging.root.setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(maintenance_router)

sentry_sdk.init(AppConfig.sentry_dsn_cron(), traces_sample_rate=1.0)
