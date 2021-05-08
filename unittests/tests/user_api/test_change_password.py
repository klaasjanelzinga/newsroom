import pytest
from faker import Faker
from fastapi import HTTPException

from api.user_api import UserChangePasswordRequest, change_password_user, UserSignInRequest, sign_in_user
from core_lib.application_data import Repositories
from core_lib.repositories import User


@pytest.mark.asyncio
async def test_change_password(
    repositories: Repositories,
    faker: Faker,
    approved_up_user: User,
    approved_up_user_password: str,
    approved_up_bearer_token: str,
):
    new_password = faker.password(length=16, special_chars=True, digits=True, upper_case=True, lower_case=True)
    request = UserChangePasswordRequest(
        email_address=approved_up_user.email_address,
        current_password=approved_up_user_password,
        new_password=new_password,
        new_password_repeated=new_password,
    )
    await change_password_user(request, authorization=approved_up_bearer_token)

    # Sign in using new password
    request = UserSignInRequest(email_address=approved_up_user.email_address, password=new_password)
    response = await sign_in_user(request)
    assert response is not None

    # Sign in using old password -> fail 401
    with pytest.raises(HTTPException) as http_exception:
        await sign_in_user(
            UserSignInRequest(email_address=approved_up_user.email_address, password=approved_up_user_password)
        )
    assert http_exception.value.status_code == 401
    assert http_exception.value.detail == "Unauthorized"


@pytest.mark.asyncio
async def test_change_password_non_existing_user(
    repositories: Repositories,
    approved_up_user: User,
    approved_up_user_password: str,
    approved_up_bearer_token: str,
):
    with pytest.raises(HTTPException) as http_exception:
        request = UserChangePasswordRequest(
            email_address=f"non-existing-{approved_up_user.email_address}",
            current_password=approved_up_user_password,
            new_password=f"new-{approved_up_user_password}",
            new_password_repeated=f"new-{approved_up_user_password}",
        )
        await change_password_user(request, authorization=approved_up_bearer_token)
    assert http_exception.value.status_code == 401
    assert http_exception.value.detail == ""


@pytest.mark.asyncio
async def test_change_password_weak_passwords(
    repositories: Repositories,
    approved_up_user: User,
    approved_up_user_password: str,
    approved_up_bearer_token: str,
):
    for weak_password in ["shortie", "nocaps(@#*$&9879", "NOLOWER293874@(#*&$", "NoSDigits(@#*&$", "NoSpecials2897365"]:
        request = UserChangePasswordRequest(
            email_address=approved_up_user.email_address,
            current_password=approved_up_user_password,
            new_password=weak_password,
            new_password_repeated=weak_password,
        )
        response = await change_password_user(request, authorization=approved_up_bearer_token)
        assert not response.success
        assert response.message.startswith("Password must")


@pytest.mark.asyncio
async def test_change_password_non_matching_passwords(
    repositories: Repositories,
    faker: Faker,
    approved_up_user: User,
    approved_up_user_password: str,
    approved_up_bearer_token: str,
):
    new_password = faker.password(length=16, special_chars=True, digits=True, upper_case=True, lower_case=True)
    request = UserChangePasswordRequest(
        email_address=approved_up_user.email_address,
        current_password=approved_up_user_password,
        new_password=new_password,
        new_password_repeated=f"non-{new_password}",
    )
    response = await change_password_user(request, authorization=approved_up_bearer_token)
    assert not response.success
    assert response.message == "Passwords do not match"
