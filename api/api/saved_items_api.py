from typing import List, Optional

from fastapi import APIRouter, Header
from pydantic.main import BaseModel
from starlette.status import HTTP_200_OK

from api.api_application_data import security
from core_lib.repositories import SavedNewsItem
from core_lib.saved_news_items import (
    delete_saved_news_item_with_id,
    fetch_saved_news_item_for_user,
    save_news_item_from_news_item,
)

saved_news_router = APIRouter()


class SavedNewsItemsResponse(BaseModel):
    saved_news: List[SavedNewsItem]
    token: str


class SaveNewsItemRequest(BaseModel):
    news_item_id: str


class SaveNewsItemResponse(BaseModel):
    saved_news_item_id: str


class ScrollableResult(BaseModel):
    token: str
    items: List


@saved_news_router.get(
    "/saved-news",
    tags=["saved-news"],
    response_model=ScrollableResult,
    responses={
        HTTP_200_OK: {"model": ScrollableResult, "description": "List is complete"},
    },
)
async def get_saved_news_items(
    fetch_offset: str = None, authorization: Optional[str] = Header(None)
) -> ScrollableResult:
    user = await security.get_approved_user(authorization)

    cursor = bytes(fetch_offset, "utf-8") if fetch_offset is not None else None
    token, result = fetch_saved_news_item_for_user(user=user, cursor=cursor)

    return ScrollableResult(items=result, token=token)


@saved_news_router.post(
    "/saved-news",
    tags=["saved-news"],
    response_model=SaveNewsItemResponse,
    responses={HTTP_200_OK: {"model": SaveNewsItemResponse, "Description": "News Item successfully saved"}},
)
async def save_news_item(
    save_news_request: SaveNewsItemRequest, authorization: Optional[str] = Header(None)
) -> SaveNewsItemResponse:
    user = await security.get_approved_user(authorization)
    saved_news_item = save_news_item_from_news_item(save_news_request.news_item_id, user)
    return SaveNewsItemResponse(saved_news_item_id=saved_news_item.saved_news_item_id)


@saved_news_router.delete(
    "/saved-news/{saved_news_item_id}",
    tags=["saved-news"],
    responses={HTTP_200_OK: {"model": SaveNewsItemResponse, "Description": "News Item successfully saved"}},
)
async def delete_saved_news_item(saved_news_item_id: str, authorization: Optional[str] = Header(None)) -> None:
    user = await security.get_approved_user(authorization)
    delete_saved_news_item_with_id(saved_news_item_id, user)
