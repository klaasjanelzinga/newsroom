import logging

from fastapi import FastAPI

from cron.maintenance_api import maintenance_router

logging.root.setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(maintenance_router)
