import logging
from typing import Optional

from fastapi import APIRouter, Response, Header
from pydantic.main import BaseModel
from starlette import status

from api.api_application_data import security
from api.api_utils import ErrorMessage
from api.security import TokenVerifier
from core_lib.application_data import user_repository
from core_lib.user import User

user_router = APIRouter()
logger = logging.getLogger(__name__)


@user_router.post(
    "/user/signup",
    tags=["user"],
    response_model=User,
    responses={
        status.HTTP_201_CREATED: {
            "model": User,
            "description": "The user is created and logged in.",
        },
        status.HTTP_200_OK: {"model": User, "description": "The user is logged in.",},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorMessage},
    },
)
async def signup(
    response: Response, authorization: Optional[str] = Header(None)
) -> User:
    """
    Either login or sign the user up (create)  for this service.

    :param response: The response object from FastAPI.
    :param authorization: The authorization bearer.
    :return: User object with user details.
    """
    user_from_token = await TokenVerifier.verify(authorization)
    user = user_repository.fetch_user_by_email(email=user_from_token.email)
    if user is None:
        user = user_repository.upsert(user_from_token)
        response.status_code = status.HTTP_201_CREATED
        return user
    response.status_code = status.HTTP_200_OK
    return user


@user_router.get(
    "/user",
    tags=["user"],
    response_model=User,
    responses={
        status.HTTP_200_OK: {
            "model": ErrorMessage,
            "description": "The user is logged in.",
        },
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorMessage},
        status.HTTP_403_FORBIDDEN: {"model": ErrorMessage},
    },
)
async def fetch_user(authorization: Optional[str] = Header(None)) -> User:
    """ Fetches all the details of the user. """
    user = await security.get_approved_user(authorization)
    return user


class UpdateUserProfileRequest(BaseModel):
    given_name: str
    family_name: str


@user_router.post(
    "/user/profile",
    summary="Updates the mutable details of the logged in user",
    tags=["user"],
    response_model=User,
    responses={
        status.HTTP_200_OK: {
            "model": User,
            "description": "The user profile is updated",
        },
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorMessage},
        status.HTTP_403_FORBIDDEN: {"model": ErrorMessage},
    },
)
async def update_user_profile(
    updated_user_request: UpdateUserProfileRequest,
    authorization: Optional[str] = Header(None),
) -> User:
    user = await security.get_approved_user(authorization)
    user.given_name = updated_user_request.given_name
    user.family_name = updated_user_request.family_name
    user_repository.upsert(user)
    return user
