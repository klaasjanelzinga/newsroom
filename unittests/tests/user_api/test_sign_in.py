from datetime import timedelta, datetime

import jwt
import pytest
from fastapi import HTTPException

from api.feed_api import get_all_feeds
from api.user_api import sign_in_user, UserSignInRequest
from core_lib.app_config import AppConfig
from core_lib.application_data import Repositories
from core_lib.repositories import User


@pytest.mark.asyncio
async def test_sign_in(
    repositories: Repositories,
    signed_up_user: User,
    signed_up_user_email_address: str,
    signed_up_user_password: str,
):
    user_sign_in_request = UserSignInRequest(
        email_address=signed_up_user_email_address, password=signed_up_user_password
    )
    response = await sign_in_user(user_sign_in_request)
    assert response.token is not None


@pytest.mark.asyncio
async def test_sign_in_wrong_password(
    repositories: Repositories, signed_up_user: User, signed_up_user_email_address: str, signed_up_user_password
):
    with pytest.raises(HTTPException) as http_exception:
        user_sign_in_request = UserSignInRequest(
            email_address=signed_up_user_email_address, password=f"wrong-{signed_up_user_password}"
        )
        await sign_in_user(user_sign_in_request)
    assert http_exception is not None
    assert http_exception.value.status_code == 401


@pytest.mark.asyncio
async def test_sign_in_wrong_user(
    repositories: Repositories,
    signed_up_user: User,
    signed_up_user_email_address: str,
    signed_up_user_password: str,
):
    with pytest.raises(HTTPException) as http_exception:
        user_sign_in_request = UserSignInRequest(
            email_address=f"wrong{signed_up_user_email_address}", password=signed_up_user_password
        )
        await sign_in_user(user_sign_in_request)
    assert http_exception is not None
    assert http_exception.value.status_code == 401


@pytest.mark.asyncio
async def test_sign_in_tampered_token(
    repositories: Repositories,
    approved_up_user: User,
    approved_up_user_email_address: str,
    approved_up_user_password: str,
):
    user_sign_in_request = UserSignInRequest(
        email_address=approved_up_user_email_address, password=approved_up_user_password
    )
    response = await sign_in_user(user_sign_in_request)
    token = f"Bearer {response.token}"
    await get_all_feeds(authorization=token)
    with pytest.raises(HTTPException) as http_exception:
        await get_all_feeds(authorization=f"s-{token}")
    assert http_exception.value.status_code == 401

    # construct some other token.
    decoded = jwt.get_unverified_header(response.token)
    other_users_token = jwt.encode(
        {
            "name": decoded.get("name"),
            "user_id": decoded.get("user_id"),
            "exp": datetime.utcnow() + timedelta(days=7),
        },
        f"wrong-{AppConfig.token_secret_key()}",
        algorithm="HS256",
    )
    with pytest.raises(HTTPException) as http_exception:
        await get_all_feeds(authorization=other_users_token)
    assert http_exception.value.status_code == 401
