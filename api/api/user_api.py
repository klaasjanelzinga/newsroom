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
    email_address: str
    password: str
    password_repeated: str


class UserSignInRequest(BaseModel):
    email_address: str
    password: str


class UserSignInResponse(BaseModel):
    token: str
    email_address: str
    is_approved: bool


class UserChangePasswordRequest(BaseModel):
    email_address: str
    current_password: str
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
                email_address=user_sign_up_request.email_address,
                password=user_sign_up_request.password,
                password_repeated=user_sign_up_request.password_repeated,
            )
            token = TokenVerifier.create_token(user)
            return UserSignInResponse(token=token, email_address=user.email_address, is_approved=user.is_approved)
    except AuthorizationException as authorization_exception:
        raise HTTPException(status_code=401, detail=authorization_exception.__str__()) from authorization_exception


@user_router.post(
    "/user/change_password",
    tags=["user"],
    response_model=UserSignInResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorMessage},
    },
)
async def change_password_user(user_change_password_request: UserChangePasswordRequest) -> UserSignInResponse:
    """
    Change the password for the user.
    """
    try:
        user = change_password(
            email_address=user_change_password_request.email_address,
            current_password=user_change_password_request.current_password,
            new_password=user_change_password_request.new_password,
            new_password_repeated=user_change_password_request.new_password_repeated,
        )
        token = TokenVerifier.create_token(user)
        return UserSignInResponse(token=token, email_address=user.email_address, is_approved=user.is_approved)
    except AuthorizationException as authorization_exception:
        raise HTTPException(status_code=401, detail=authorization_exception.__str__()) from authorization_exception


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
        user = sign_in(email_address=user_sign_in_request.email_address, password=user_sign_in_request.password)
        token = TokenVerifier.create_token(user)
        return UserSignInResponse(token=token, email_address=user.email_address, is_approved=user.is_approved)
    except AuthorizationException as authorization_exception:
        raise HTTPException(status_code=401) from authorization_exception
