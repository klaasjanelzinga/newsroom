import logging

from fastapi import APIRouter, HTTPException
from pydantic.main import BaseModel
from starlette import status

from api.api_utils import ErrorMessage
from api.security import TokenVerifier
from core_lib.application_data import repositories
from core_lib.exceptions import AuthorizationException
from core_lib.repositories import User
from core_lib.user import signup, sign_in, change_password

user_router = APIRouter()
logger = logging.getLogger(__name__)


class UserSignUpRequest(BaseModel):
    name: str
    password: str
    password_repeated: str


class UserSignInRequest(BaseModel):
    name: str
    password: str


class UserSignInResponse(BaseModel):
    token: str


class UserChangePasswordRequest(BaseModel):
    name: str
    old_password: str
    new_password: str
    new_password_repeated: str


@user_router.post(
    "/user/signup",
    tags=["user"],
    response_model=UserSignInResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorMessage},
    },
)
async def sign_up_user(user_sign_up_request: UserSignUpRequest) -> UserSignInResponse:
    """
    Sign up the user.
    """
    try:
        with repositories.client.transaction():
            user = signup(
                name=user_sign_up_request.name,
                password=user_sign_up_request.password,
                password_repeated=user_sign_up_request.password_repeated,
            )
            token = TokenVerifier.create_token(user)
            return UserSignInResponse(token=token)
    except AuthorizationException as ex:
        raise HTTPException(status_code=401, detail=ex.__str__()) from ex


@user_router.post(
    "/user/change_password",
    tags=["user"],
    response_model=User,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorMessage},
    },
)
async def change_password_user(user_change_password_request: UserChangePasswordRequest) -> User:
    """
    Change the password for the user.
    """
    try:
        return change_password(
            name=user_change_password_request.name,
            old_password=user_change_password_request.old_password,
            new_password=user_change_password_request.new_password,
            new_password_repeated=user_change_password_request.new_password_repeated,
        )
    except AuthorizationException as ex:
        raise HTTPException(status_code=401, detail=ex.__str__()) from ex


@user_router.post(
    "/user/signin",
    tags=["user"],
    response_model=UserSignInResponse,
    responses={
        status.HTTP_200_OK: {
            "model": User,
            "description": "The user is logged in.",
        },
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorMessage},
    },
)
async def sign_in_user(user_sign_in_request: UserSignInRequest) -> UserSignInResponse:
    try:
        user = sign_in(name=user_sign_in_request.name, password=user_sign_in_request.password)
        token = TokenVerifier.create_token(user)
        return UserSignInResponse(token=token)
    except AuthorizationException:
        raise HTTPException(status_code=401)
