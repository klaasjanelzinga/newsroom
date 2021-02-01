import logging
from datetime import timedelta, datetime
from typing import Dict, Optional

import jwt
from fastapi import HTTPException
from starlette.status import HTTP_403_FORBIDDEN, HTTP_401_UNAUTHORIZED

from core_lib.repositories import User, UserRepository
from core_lib.utils import bytes_to_str_base64


class TokenVerificationException(Exception):
    pass


log = logging.getLogger(__file__)

secret_key = "secret"


class TokenVerifier:
    @staticmethod
    async def verify(bearer_token: Optional[str]) -> Dict[str, str]:
        """
        Verifies the bearer token.

        :param bearer_token: The content of the authorization header.
        :return: A User object constructed from the token with is_approved set to False.
        :raises HTTPException: If the authorization from the token failed.

        """
        if bearer_token is None:
            raise HTTPException(status_code=401, detail="Unauthorized")
        if not isinstance(bearer_token, str):
            raise HTTPException(status_code=401, detail="Unauthorized")
        if len(bearer_token) < 15:
            raise HTTPException(status_code=401, detail="Unauthorized")
        if not bearer_token.startswith("Bearer"):
            raise HTTPException(status_code=401, detail="Unauthorized")
        token = bearer_token[7:]
        decoded = jwt.decode(token, secret_key, "HS256")
        return decoded

    @staticmethod
    def create_token(user: User) -> str:
        return jwt.encode(
            {
                "name": user.name,
                "user_id": user.user_id,
                "exp": datetime.utcnow() + timedelta(days=7),
            },
            secret_key,
            algorithm="HS256",
        )


class Security:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def get_approved_user(self, authorization_header: Optional[str]) -> User:
        """
        Does the token verification and retrieves the user object from the repository. If the user is not approved a
        403 FORBIDDEN is returned.
        """
        user_from_token = await TokenVerifier.verify(authorization_header)
        user_from_repo = self.user_repository.fetch_user_by_name(user_from_token["name"])
        if user_from_repo is None:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)
        if not user_from_repo.is_approved:
            raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="User is not yet approved")
        return user_from_repo
