import logging
from typing import List, Optional

from fastapi import APIRouter, Header
from pydantic.main import BaseModel
from starlette.status import HTTP_200_OK

from api.api_application_data import security
from core_lib.application_data import repositories
from core_lib.repositories import NewsItem

news_router = APIRouter()
log = logging.getLogger(__name__)


class NewsItemListResponse(BaseModel):
    news_items: List[NewsItem]
    number_of_unread_items: int


class ReadNewsItemListResponse(BaseModel):
    token: str
    news_items: List[NewsItem]


@news_router.get(
    "/news-items",
    tags=["news-items"],
    response_model=NewsItemListResponse,
    responses={HTTP_200_OK: {"model": NewsItemListResponse, "description": "List is complete"}},
)
async def news_items(
    fetch_offset: int, fetch_limit: int = 30, authorization: Optional[str] = Header(None)
) -> NewsItemListResponse:
    """Fetch the next set of news items."""
    fetch_limit = min(fetch_limit, 80)
    user = await security.get_approved_user(authorization)
    result = await repositories.news_item_repository.fetch_items(user=user, offset=fetch_offset, limit=fetch_limit)

    return NewsItemListResponse(news_items=result, number_of_unread_items=user.number_of_unread_items)


@news_router.get(
    "/news-items/read",
    tags=["news-items"],
    response_model=ReadNewsItemListResponse,
    responses={HTTP_200_OK: {"model": ReadNewsItemListResponse, "description": "List is complete"}},
)
async def read_news_items(
    fetch_offset: str = None, authorization: Optional[str] = Header(None)
) -> ReadNewsItemListResponse:
    """Fetch the next set of news items."""
    user = await security.get_approved_user(authorization)
    cursor = bytes(fetch_offset, "utf-8") if fetch_offset is not None else None
    token, result = repositories.news_item_repository.fetch_read_items(user=user, cursor=cursor, limit=30)

    return ReadNewsItemListResponse(token=token, news_items=result)


class MarkAsReadRequest(BaseModel):
    news_item_ids: List[str]


@news_router.post("/news-items/mark-as-read", tags=["news-items"])
async def mark_as_read(mark_as_read_request: MarkAsReadRequest, authorization: Optional[str] = Header("")) -> None:
    user = await security.get_approved_user(authorization)
    repositories.news_item_repository.mark_items_as_read(user=user, news_item_ids=mark_as_read_request.news_item_ids)
    user.number_of_unread_items = max(0, user.number_of_unread_items - len(mark_as_read_request.news_item_ids))
    repositories.user_repository.upsert(user)
