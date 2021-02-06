import pytest
from faker import Faker
from fastapi import HTTPException

from api.user_api import UserChangePasswordRequest, change_password_user, UserSignInRequest, sign_in_user
from core_lib.repositories import User
from tests.mock_repositories import MockRepositories


@pytest.mark.asyncio
async def test_change_password(repositories: MockRepositories, faker: Faker, signed_up_user: User, user_password: str):
    new_password = faker.password(length=16, special_chars=True, digits=True, upper_case=True, lower_case=True)
    request = UserChangePasswordRequest(
        email_address=signed_up_user.email_address,
        current_password=user_password,
        new_password=new_password,
        new_password_repeated=new_password,
    )
    response = await change_password_user(request)
    assert response.email_address == signed_up_user.email_address
    assert response.is_approved == signed_up_user.is_approved
    assert response.token is not None

    # Sign in using new password
    request = UserSignInRequest(email_address=signed_up_user.email_address, password=new_password)
    response = await sign_in_user(request)
    assert response is not None

    # Sign in using old password -> fail 401
    with pytest.raises(HTTPException) as http_exception:
        await sign_in_user(UserSignInRequest(email_address=signed_up_user.email_address, password=user_password))
    assert http_exception.value.status_code == 401


@pytest.mark.asyncio
async def test_change_password_non_existing_user(
    repositories: MockRepositories, signed_up_user: User, user_password: str
):
    with pytest.raises(HTTPException) as http_exception:
        request = UserChangePasswordRequest(
            email_address=f"non-existing-{signed_up_user.email_address}",
            current_password=user_password,
            new_password=f"new-{user_password}",
            new_password_repeated=f"new-{user_password}",
        )
        await change_password_user(request)
    assert http_exception.value.status_code == 401


@pytest.mark.asyncio
async def test_change_password_weak_passwords(repositories: MockRepositories, signed_up_user: User, user_password: str):
    for weak_password in ["shortie", "nocaps(@#*$&9879", "NOLOWER293874@(#*&$", "NoSDigits(@#*&$", "NoSpecials2897365"]:
        with pytest.raises(HTTPException) as http_exception:
            request = UserChangePasswordRequest(
                email_address=signed_up_user.email_address,
                current_password=user_password,
                new_password=weak_password,
                new_password_repeated=weak_password,
            )
            await change_password_user(request)
        assert http_exception.value.status_code == 401


@pytest.mark.asyncio
async def test_change_password_non_matching_passwords(
    repositories: MockRepositories, faker: Faker, signed_up_user: User, user_password: str
):
    new_password = faker.password(length=16, special_chars=True, digits=True, upper_case=True, lower_case=True)
    request = UserChangePasswordRequest(
        email_address=signed_up_user.email_address,
        current_password=user_password,
        new_password=new_password,
        new_password_repeated=f"non-{new_password}",
    )
    with pytest.raises(HTTPException) as http_exception:
        await change_password_user(request)
