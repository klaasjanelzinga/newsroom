from typing import List, Optional

from bson import ObjectId
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

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        by_alias = False
        json_encoders = {ObjectId: str}


class SaveNewsItemRequest(BaseModel):
    news_item_id: str


class SaveNewsItemResponse(BaseModel):
    saved_news_item_id: str


class ScrollableResult(BaseModel):
    items: List

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        by_alias = False
        json_encoders = {ObjectId: str}


@saved_news_router.get(
    "/saved-news",
    tags=["saved-news"],
    response_model=ScrollableResult,
    responses={
        HTTP_200_OK: {"model": ScrollableResult, "description": "List is complete"},
    },
)
async def get_saved_news_items(fetch_offset: int, fetch_limit: int, authorization: Optional[str] = Header(None)) -> ScrollableResult:
    user = await security.get_approved_user(authorization)
    limit = min(fetch_limit, 30)

    result = await fetch_saved_news_item_for_user(user=user, offset=fetch_offset, limit=limit)

    return ScrollableResult(items=result)


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
    saved_news_item = await save_news_item_from_news_item(save_news_request.news_item_id, user)
    return SaveNewsItemResponse(saved_news_item_id=saved_news_item.saved_news_item_id.__str__())


@saved_news_router.delete(
    "/saved-news/{saved_news_item_id}",
    tags=["saved-news"],
    responses={HTTP_200_OK: {"model": SaveNewsItemResponse, "Description": "News Item successfully saved"}},
)
async def delete_saved_news_item(saved_news_item_id: str, authorization: Optional[str] = Header(None)) -> None:
    user = await security.get_approved_user(authorization)
    await delete_saved_news_item_with_id(saved_news_item_id, user)
