from fastapi import APIRouter
from pydantic.main import BaseModel

from core_lib.feed import refresh_rss_feeds

maintenance_router = APIRouter()


class RefreshAllFeedsResponse(BaseModel):
    number_of_feeds_refreshed: int


@maintenance_router.get("/maintenance/refresh-rss-feeds", tags=["maintenance"])
async def refresh_all_feeds() -> RefreshAllFeedsResponse:
    number_of_refreshed_feeds = await refresh_rss_feeds()
    return RefreshAllFeedsResponse(number_of_feeds_refreshed=number_of_refreshed_feeds)
