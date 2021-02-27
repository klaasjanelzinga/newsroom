from fastapi import APIRouter
from pydantic.main import BaseModel

from core_lib.feed import delete_read_items, update_number_items_in_feeds
from core_lib.rss_feed import refresh_all_feeds

maintenance_router = APIRouter()


class RefreshAllFeedsResponse(BaseModel):
    number_of_feeds_refreshed: int


class DeleteReadResponse(BaseModel):
    number_of_items_deleted: int


@maintenance_router.get("/maintenance/refresh-feeds", tags=["maintenance"])
async def do_refresh_all_feeds() -> RefreshAllFeedsResponse:
    number_of_refreshed_feeds = await refresh_all_feeds()
    return RefreshAllFeedsResponse(number_of_feeds_refreshed=number_of_refreshed_feeds)


@maintenance_router.get("/maintenance/delete-read-items", tags=["maintenance"])
def delete_read_feed_items() -> DeleteReadResponse:
    number_of_deleted_items = delete_read_items()
    update_number_items_in_feeds()
    return DeleteReadResponse(number_of_items_deleted=number_of_deleted_items)
