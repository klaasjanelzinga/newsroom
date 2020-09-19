from fastapi import APIRouter
from pydantic.main import BaseModel

from core_lib.feed import refresh_rss_feeds, delete_read_items

maintenance_router = APIRouter()


class RefreshAllFeedsResponse(BaseModel):
    number_of_feeds_refreshed: int


class DeleteReadResponse(BaseModel):
    number_of_items_deleted: int


@maintenance_router.get("/maintenance/refresh-rss-feeds", tags=["maintenance"])
async def refresh_all_feeds() -> RefreshAllFeedsResponse:
    number_of_refreshed_feeds = await refresh_rss_feeds()
    return RefreshAllFeedsResponse(number_of_feeds_refreshed=number_of_refreshed_feeds)


@maintenance_router.get("/maintenance/delete-read-items", tags=["maintenance"])
async def delete_read_feed_items() -> DeleteReadResponse:
    number_of_deleted_items = await delete_read_items()
    return DeleteReadResponse(number_of_items_deleted=number_of_deleted_items)
