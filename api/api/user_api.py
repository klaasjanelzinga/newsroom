import logging
from typing import Dict, Optional

import aiohttp
from fastapi import APIRouter, Header, HTTPException
from google.auth import jwt
from pydantic.main import BaseModel
from starlette import status

user_router = APIRouter()
logger = logging.getLogger(__name__)


class User(BaseModel):
    given_name: str
    family_name: str
    email: str
    avatar_url: str


class ErrorMessage(BaseModel):
    detail: str


class TokenVerificationException(Exception):
    pass


class TokenVerifier:
    @staticmethod
    async def _fetch_certs() -> Dict:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as task_session:
            async with task_session.get(
                "https://www.googleapis.com/oauth2/v1/certs"
            ) as response:
                return await response.json()

    @staticmethod
    async def verify(bearer_token: Optional[str]) -> User:
        token_certs = TokenVerifier._fetch_certs()
        try:
            if bearer_token is None:
                raise TokenVerificationException("Authorization header is not set")
            if len(bearer_token) < 15:
                raise TokenVerificationException(
                    "Unlikely content of authorization header"
                )
            if not bearer_token.startswith("Bearer"):
                raise TokenVerificationException(
                    "Unlikely content of authorization header"
                )
            token = bearer_token[7:]
            result = jwt.decode(
                token=token,
                certs=await token_certs,
                audience="662875567592-9do93u1nppl2ks4geufjtm7n5hfo23m3.apps.googleusercontent.com",
            )
            return User(
                given_name=result["given_name"],
                family_name=result["family_name"],
                email=result["email"],
                avatar_url=result["picture"],
            )
        except ValueError as error:
            raise TokenVerificationException(error.__str__())


@user_router.post(
    "/user/signup",
    response_model=User,
    responses={
        status.HTTP_201_CREATED: {"model": ErrorMessage},
        status.HTTP_200_OK: {"model": ErrorMessage},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorMessage},
    },
)
async def signup(authorization: Optional[str] = Header(None)) -> User:
    """
    Either login or sign the user up (create)  for this service.

    :param authorization: The authorization bearer.
    :return: User object with user details.
    """
    try:
        return await TokenVerifier.verify(authorization)
    except TokenVerificationException as tve:
        logging.warning("Unable to verify jwt: %s", tve.__str__())
        raise HTTPException(status_code=401, detail="Unauthorized")
