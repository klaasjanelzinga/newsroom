import pytest
from fastapi import HTTPException

from api.user_api import sign_in_user, UserSignInRequest
from core_lib.repositories import User
from tests.mock_repositories import MockRepositories


@pytest.mark.asyncio
async def test_signin(repositories: MockRepositories, signed_up_user: User, user_name: str, user_password: str):
    user_sign_in_request = UserSignInRequest(name=user_name, password=user_password)
    response = await sign_in_user(user_sign_in_request)
    assert response.token is not None


@pytest.mark.asyncio
async def test_signin_wrong_password(
    repositories: MockRepositories, signed_up_user: User, user_name: str, user_password: str
):
    with pytest.raises(HTTPException) as http_exception:
        user_sign_in_request = UserSignInRequest(name=user_name, password=f"wrong-{user_password}")
        await sign_in_user(user_sign_in_request)
    assert http_exception is not None
    assert http_exception.value.status_code == 401


@pytest.mark.asyncio
async def test_signin_wrong_user(
    repositories: MockRepositories, signed_up_user: User, user_name: str, user_password: str
):
    with pytest.raises(HTTPException) as http_exception:
        user_sign_in_request = UserSignInRequest(name=f"wrong{user_name}", password=user_password)
        await sign_in_user(user_sign_in_request)
    assert http_exception is not None
    assert http_exception.value.status_code == 401
