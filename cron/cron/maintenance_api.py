from fastapi import APIRouter
from pydantic.main import BaseModel

from core_lib.atom_feed import refresh_atom_feeds
from core_lib.feed import delete_read_items
from core_lib.html_feed import refresh_html_feeds
from core_lib.rss_feed import refresh_rss_feeds

maintenance_router = APIRouter()


class RefreshAllFeedsResponse(BaseModel):
    number_of_feeds_refreshed: int


class DeleteReadResponse(BaseModel):
    number_of_items_deleted: int


@maintenance_router.get("/maintenance/refresh-rss-feeds", tags=["maintenance"])
async def refresh_all_rss_feeds() -> RefreshAllFeedsResponse:
    number_of_refreshed_feeds = await refresh_rss_feeds()
    return RefreshAllFeedsResponse(number_of_feeds_refreshed=number_of_refreshed_feeds)


@maintenance_router.get("/maintenance/delete-read-items", tags=["maintenance"])
async def delete_read_feed_items() -> DeleteReadResponse:
    number_of_deleted_items = await delete_read_items()
    return DeleteReadResponse(number_of_items_deleted=number_of_deleted_items)


@maintenance_router.get("/maintenance/refresh-html-feeds", tags=["maintenance"])
async def refresh_all_html_feeds() -> RefreshAllFeedsResponse:
    number_of_refreshed_feeds = await refresh_html_feeds()
    return RefreshAllFeedsResponse(number_of_feeds_refreshed=number_of_refreshed_feeds)


@maintenance_router.get("/maintenance/refresh-atom-feeds", tags=["maintenance"])
async def refresh_all_atom_feeds() -> RefreshAllFeedsResponse:
    number_of_refreshed_feeds = await refresh_atom_feeds()
    return RefreshAllFeedsResponse(number_of_feeds_refreshed=number_of_refreshed_feeds)
