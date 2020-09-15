import logging
from typing import Optional, List

from fastapi import APIRouter, Header
from pydantic.main import BaseModel
from starlette.status import HTTP_200_OK

from api.api_application_data import security
from core_lib.application_data import repositories
from core_lib.repositories import NewsItem

news_router = APIRouter()
log = logging.getLogger(__name__)


class NewsItemListResponse(BaseModel):
    token: str
    news_items: List[NewsItem]


@news_router.get(
    "/news-items",
    tags=["news-items"],
    response_model=NewsItemListResponse,
    responses={HTTP_200_OK: {"model": NewsItemListResponse, "description": "List is complete"}},
)
async def news_items(fetch_offset: str = None, authorization: Optional[str] = Header(None)) -> NewsItemListResponse:
    """ Fetch the next set of news items. """
    user = await security.get_approved_user(authorization)
    cursor = bytes(fetch_offset, "utf-8") if fetch_offset is not None else None
    token, result = repositories.news_item_repository.fetch_items(user=user, cursor=cursor, limit=30)

    return NewsItemListResponse(token=token, news_items=result)


@news_router.get(
    "/news-items/read",
    tags=["news-items"],
    response_model=NewsItemListResponse,
    responses={HTTP_200_OK: {"model": NewsItemListResponse, "description": "List is complete"}},
)
async def read_news_items(
    fetch_offset: str = None, authorization: Optional[str] = Header(None)
) -> NewsItemListResponse:
    """ Fetch the next set of news items. """
    user = await security.get_approved_user(authorization)
    cursor = bytes(fetch_offset, "utf-8") if fetch_offset is not None else None
    token, result = repositories.news_item_repository.fetch_read_items(user=user, cursor=cursor, limit=30)

    return NewsItemListResponse(token=token, news_items=result)


class MarkAsReadRequest(BaseModel):
    news_item_ids: List[str]


@news_router.post("/news-items/mark-as-read", tags=["news-items"])
async def mark_as_read(mark_as_read_request: MarkAsReadRequest, authorization: Optional[str] = Header(None)) -> None:
    user = await security.get_approved_user(authorization)
    repositories.news_item_repository.mark_items_as_read(user=user, news_item_ids=mark_as_read_request.news_item_ids)
