import logging

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api.feed_api import feed_router
from api.user_api import user_router

logging.root.setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)

app = FastAPI()


origins = [
    "http://localhost:4000",
    "https://newsroom.n-kj.nl",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(feed_router)
