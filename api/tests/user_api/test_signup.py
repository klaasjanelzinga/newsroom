from unittest.mock import patch, Mock, MagicMock, AsyncMock

import pytest
from faker import Faker

from api.user_api import signup
from core_lib.application_data import Repositories
from core_lib.repositories import User


@pytest.mark.asyncio
@patch("api.user_api.TokenVerifier")
async def test_signup_new_user(security_mock: Mock, faker: Faker, user: User, repositories: Repositories):
    user.is_approved = False
    security_mock.verify = AsyncMock()
    security_mock.verify.return_value = user
    repositories.mock_user_repository().fetch_user_by_email.return_value = None

    security_mock.return_value = user
    response_mock = MagicMock()

    response = await signup(response_mock, authorization=faker.word())
    assert response_mock.status_code == 201

    assert not response.is_approved
    assert response.email == user.email
    assert response.family_name == user.family_name

    repositories.user_repository.upsert.assert_called_once()


@pytest.mark.asyncio
@patch("api.user_api.TokenVerifier")
async def test_signup_existing_user(security_mock: Mock, faker: Faker, user: User, repositories: Repositories):
    user.is_approved = False
    security_mock.verify = AsyncMock()
    security_mock.verify.return_value = user
    repositories.mock_user_repository().fetch_user_by_email.return_value = user

    security_mock.return_value = user
    response_mock = MagicMock()

    response = await signup(response_mock, authorization=faker.word())
    assert response_mock.status_code == 200

    assert not response.is_approved
    repositories.user_repository.upsert.assert_not_called()
