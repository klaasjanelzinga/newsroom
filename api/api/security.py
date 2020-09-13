import logging
from asyncio.tasks import Task
from typing import Dict, Optional

import aiohttp
from fastapi import HTTPException
from google.auth import jwt
from starlette.status import HTTP_403_FORBIDDEN

from core_lib.repositories import User, UserRepository


class TokenVerificationException(Exception):
    pass


log = logging.getLogger(__file__)


class TokenVerifier:
    @staticmethod
    async def _fetch_certs() -> Dict:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as task_session:
            async with task_session.get("https://www.googleapis.com/oauth2/v1/certs") as response:
                return await response.json()

    @staticmethod
    async def verify(bearer_token: Optional[str]) -> User:
        """
        Verifies the bearer token.

        :param bearer_token: The content of the authorization header.
        :return: A User object constructed from the token with is_approved set to False.
        :raises Http

        """
        token_certs = Task(TokenVerifier._fetch_certs())
        try:
            if bearer_token is None:
                token_certs.cancel()
                raise HTTPException(status_code=401, detail="Unauthorized")
            if len(bearer_token) < 15:
                token_certs.cancel()
                raise HTTPException(status_code=401, detail="Unauthorized")
            if not bearer_token.startswith("Bearer"):
                token_certs.cancel()
                raise HTTPException(status_code=401, detail="Unauthorized")
            token = bearer_token[7:]
            log.info("Verifying token")
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
                is_approved=False,
            )
        except ValueError as error:
            raise HTTPException(status_code=401, detail=error.__str__()) from error


class Security:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def get_approved_user(self, authorization_header: Optional[str]) -> User:
        """
        Does the token verification and retrieves the user object from the repository. If the user is not approved a
        403 FORBIDDEN is returned.
        """
        user_from_token = await TokenVerifier.verify(authorization_header)
        user_from_repo = self.user_repository.fetch_user_by_email(user_from_token.email)
        if not user_from_repo.is_approved:
            raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="User is not yet approved")
        return user_from_repo
