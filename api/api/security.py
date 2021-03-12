from datetime import datetime, timedelta
import logging
from typing import Dict, Optional

from fastapi import HTTPException
import jwt
from jwt import PyJWTError
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from core_lib import application_data
from core_lib.repositories import User, UserRepository

log = logging.getLogger(__file__)


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
        try:
            return jwt.decode(jwt=token, key=application_data.token_secret_key, algorithms=["HS256"])
        except ValueError as value_error:
            raise HTTPException(status_code=401, detail="Unauthorized") from value_error
        except PyJWTError as jwt_error:
            raise HTTPException(status_code=401, detail="Unauthorized") from jwt_error

    @staticmethod
    def create_token(user: User, token_verified: bool = False) -> str:
        return jwt.encode(
            payload={
                "name": user.email_address,
                "user_id": user.user_id,
                "otp_verified": token_verified,
                "exp": datetime.utcnow() + timedelta(days=7),
            },
            key=application_data.token_secret_key,
            algorithm="HS256",
        )


class Security:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def get_approved_user(self, authorization_header: Optional[str], check_totp: bool = True) -> User:
        """
        Does the token verification and retrieves the user object from the repository. If the user is not approved a
        403 FORBIDDEN is returned.
        """
        user_from_token = await TokenVerifier.verify(authorization_header)
        user_from_repo = self.user_repository.fetch_user_by_email(user_from_token["name"])
        if user_from_repo is None:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)
        if check_totp and user_from_repo.otp_hash is not None and not user_from_token["otp_verified"]:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)
        if not user_from_repo.is_approved:
            raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="User is not yet approved")
        return user_from_repo
