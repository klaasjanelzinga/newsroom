import logging
from typing import List, Optional

from fastapi import APIRouter, Header, Response, HTTPException
from pydantic.main import BaseModel
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST

from api.api_application_data import security
from api.api_utils import ErrorMessage
from core_lib.application_data import repositories
from core_lib.feed import (
    fetch_feed_information_for,
    subscribe_user_to_feed,
    NetworkingException,
    unsubscribe_user_from_feed,
)
from core_lib.repositories import Feed, User

feed_router = APIRouter()
logger = logging.getLogger(__name__)


class FeedWithSubscriptionInformationResponse(BaseModel):
    feed: Feed
    user_is_subscribed: bool


@feed_router.post(
    "/feeds/for_url",
    tags=["feed"],
    response_model=FeedWithSubscriptionInformationResponse,
    responses={
        HTTP_201_CREATED: {
            "model": Feed,
            "description": "Feed was unknown and is created.",
        },
        HTTP_200_OK: {
            "model": Feed,
            "description": "Feed is known.",
        },
        HTTP_404_NOT_FOUND: {"model": ErrorMessage},
    },
)
async def fetch_feed_information_for_url(
    response: Response, url: str, authorization: Optional[str] = Header(None)
) -> FeedWithSubscriptionInformationResponse:
    """
    If the feed is known in the system (by url), return this information. If the feed is unknown retrieve the url
    and create a new Feed Entity. Return this entity.
    """
    user = await security.get_approved_user(authorization)
    feed = repositories.feed_repository.find_by_url(url)
    if feed is not None:
        response.status_code = HTTP_200_OK
        return FeedWithSubscriptionInformationResponse(feed=feed, user_is_subscribed=feed.feed_id in user.subscribed_to)

    # find location, and store information.
    try:
        feed = await fetch_feed_information_for(session=repositories.client_session, url=url)
        if feed is None:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"No feed with url {url} found")
        response.status_code = HTTP_201_CREATED
        return FeedWithSubscriptionInformationResponse(feed=feed, user_is_subscribed=feed.feed_id in user.subscribed_to)
    except NetworkingException as networking_exception:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail=networking_exception.__str__()
        ) from networking_exception


@feed_router.get("/feeds", tags=["feed"])
async def get_all_feeds(
    authorization: Optional[str] = Header(None),
) -> List[FeedWithSubscriptionInformationResponse]:
    user = await security.get_approved_user(authorization)
    subscribed_feed_ids = user.subscribed_to
    feeds = repositories.feed_repository.all_feeds()
    return [
        FeedWithSubscriptionInformationResponse(feed=feed, user_is_subscribed=feed.feed_id in subscribed_feed_ids)
        for feed in feeds
    ]


@feed_router.post("/feeds/{feed_id}/subscribe", tags=["feed"])
async def subscribe_to_feed(feed_id: str, authorization: Optional[str] = Header(None)) -> User:
    """
    Subscribe the user to the feed with feed_id. If the user is already subscribed, nothing is done.

    :param feed_id: id of the feed.
    :param authorization: Token of the user.
    """
    user = await security.get_approved_user(authorization)
    feed = repositories.feed_repository.get(feed_id)
    user = subscribe_user_to_feed(user=user, feed=feed)
    return user


@feed_router.post("/feeds/{feed_id}/unsubscribe", tags=["feed"])
async def unsubscribe_from_feed(feed_id: str, authorization: Optional[str] = Header(None)) -> User:
    """
    Unsubscribe the user from the feed with feed_id. If the user is not subscribed, noting is done.

    :param feed_id: id of the feed.
    :param authorization: Token of the user.
    """
    user = await security.get_approved_user(authorization)
    feed = repositories.feed_repository.get(feed_id)
    user = unsubscribe_user_from_feed(user=user, feed=feed)
    return user
