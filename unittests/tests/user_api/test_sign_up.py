import pytest
from faker import Faker
from fastapi import HTTPException

from api.user_api import sign_up_user, UserSignUpRequest
from core_lib.application_data import Repositories
from core_lib.repositories import User


@pytest.mark.asyncio
async def test_signup_new_user(faker: Faker, repositories: Repositories):
    email_address = faker.email()
    password = faker.password(length=16, special_chars=True, digits=True, upper_case=True, lower_case=True)

    request = UserSignUpRequest(email_address=email_address, password=password, password_repeated=password)
    response = await sign_up_user(request)
    assert response is not None
    assert response.token is not None
    assert await repositories.user_repository.count({}) == 1


@pytest.mark.asyncio
async def test_signup_existing_user(
    repositories: Repositories, signed_up_user: User, signed_up_user_email_address, signed_up_user_password
):
    assert await repositories.user_repository.count({}) == 1
    with pytest.raises(HTTPException) as http_exception:
        request = UserSignUpRequest(
            email_address=signed_up_user_email_address,
            password=signed_up_user_password,
            password_repeated=signed_up_user_password,
        )
        await sign_up_user(request)
    assert http_exception.value.status_code == 401


@pytest.mark.asyncio
async def test_signup_non_matching_passwords(repositories: Repositories, faker: Faker):
    email_address = faker.email()
    password = faker.password(length=16, special_chars=True, digits=True, upper_case=True, lower_case=True)

    with pytest.raises(HTTPException) as http_exception:
        request = UserSignUpRequest(
            email_address=email_address,
            password=password,
            password_repeated=f"wrong-{password}",
        )
        await sign_up_user(request)
    assert http_exception.value.status_code == 401


@pytest.mark.asyncio
async def test_password_strength(repositories: Repositories, faker: Faker()):
    user_email_address = faker.email()
    with pytest.raises(HTTPException) as http_exception:
        password = "shortie"
        request = UserSignUpRequest(email_address=user_email_address, password=password, password_repeated=password)
        await sign_up_user(request)
    assert http_exception.value.status_code == 401
    with pytest.raises(HTTPException) as http_exception:
        password = "nocapsnocaps34#$"
        request = UserSignUpRequest(email_address=user_email_address, password=password, password_repeated=password)
        await sign_up_user(request)
    assert http_exception.value.status_code == 401
    with pytest.raises(HTTPException) as http_exception:
        password = "NOLOWERNOLWER34#$"
        request = UserSignUpRequest(email_address=user_email_address, password=password, password_repeated=password)
        await sign_up_user(request)
    assert http_exception.value.status_code == 401
    with pytest.raises(HTTPException) as http_exception:
        password = "capsANDLowerNoDigits&*"
        request = UserSignUpRequest(email_address=user_email_address, password=password, password_repeated=password)
        await sign_up_user(request)
    assert http_exception.value.status_code == 401
    with pytest.raises(HTTPException) as http_exception:
        password = "capsANDLowerNoDigits"
        request = UserSignUpRequest(email_address=user_email_address, password=password, password_repeated=password)
        await sign_up_user(request)
    assert http_exception.value.status_code == 401
