import logging
from typing import Optional

from fastapi import FastAPI

from api.user_api import user_router

logging.root.setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(user_router)
