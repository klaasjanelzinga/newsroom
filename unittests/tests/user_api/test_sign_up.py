import pytest
from fastapi import HTTPException

from api.user_api import sign_up_user, UserSignUpRequest
from core_lib.repositories import User
from tests.mock_repositories import MockRepositories


@pytest.mark.asyncio
async def test_signup_new_user(user_name: str, user_password: str, repositories: MockRepositories):
    request = UserSignUpRequest(name=user_name, password=user_password, password_repeated=user_password)
    response = await sign_up_user(request)
    assert response is not None
    assert response.token is not None
    assert repositories.user_repository.count() == 1


@pytest.mark.asyncio
async def test_signup_existing_user(
    repositories: MockRepositories, signed_up_user: User, user_name: str, user_password: str
):
    assert repositories.user_repository.count() == 1
    with pytest.raises(HTTPException) as http_exception:
        request = UserSignUpRequest(name=user_name, password=user_password, password_repeated=user_password)
        await sign_up_user(request)
    assert http_exception.value.status_code == 401


@pytest.mark.asyncio
async def test_signup_non_matching_passwords(repositories: MockRepositories, user_name: str, user_password: str):
    with pytest.raises(HTTPException) as http_exception:
        request = UserSignUpRequest(name=user_name, password=user_password, password_repeated=f"wrong-{user_password}")
        await sign_up_user(request)
    assert http_exception.value.status_code == 401


@pytest.mark.asyncio
async def test_password_strength(repositories: MockRepositories, user_name: str, user_password: str):
    with pytest.raises(HTTPException) as http_exception:
        password = "shortie"
        request = UserSignUpRequest(name=user_name, password=password, password_repeated=password)
        await sign_up_user(request)
    assert http_exception.value.status_code == 401
    with pytest.raises(HTTPException) as http_exception:
        password = "nocapsnocaps34#$"
        request = UserSignUpRequest(name=user_name, password=password, password_repeated=password)
        await sign_up_user(request)
    assert http_exception.value.status_code == 401
    with pytest.raises(HTTPException) as http_exception:
        password = "NOLOWERNOLWER34#$"
        request = UserSignUpRequest(name=user_name, password=password, password_repeated=password)
        await sign_up_user(request)
    assert http_exception.value.status_code == 401
    with pytest.raises(HTTPException) as http_exception:
        password = "capsANDLowerNoDigits&*"
        request = UserSignUpRequest(name=user_name, password=password, password_repeated=password)
        await sign_up_user(request)
    assert http_exception.value.status_code == 401
    with pytest.raises(HTTPException) as http_exception:
        password = "capsANDLowerNoDigits"
        request = UserSignUpRequest(name=user_name, password=password, password_repeated=password)
        await sign_up_user(request)
    assert http_exception.value.status_code == 401
