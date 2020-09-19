from unittest.mock import patch, Mock, MagicMock, AsyncMock

import pytest
from faker import Faker

from api.user_api import signup
from core_lib.repositories import User
from tests.mock_repositories import MockRepositories


@pytest.mark.asyncio
@patch("api.user_api.TokenVerifier")
async def test_signup_new_user(security_mock: Mock, faker: Faker, user: User, repositories: MockRepositories):
    user.is_approved = False
    security_mock.verify = AsyncMock()
    security_mock.verify.return_value = user

    security_mock.return_value = user
    response_mock = MagicMock()

    response = await signup(response_mock, authorization=faker.word())
    assert response_mock.status_code == 201

    assert not response.is_approved
    assert response.email == user.email
    assert response.family_name == user.family_name

    assert repositories.user_repository.count() == 1


@pytest.mark.asyncio
@patch("api.user_api.TokenVerifier")
async def test_signup_existing_user(security_mock: Mock, faker: Faker, user: User, repositories: MockRepositories):
    user.is_approved = False
    security_mock.verify = AsyncMock()
    security_mock.verify.return_value = user
    repositories.user_repository.upsert(user)

    security_mock.return_value = user
    response_mock = MagicMock()

    response = await signup(response_mock, authorization=faker.word())
    assert response_mock.status_code == 200

    assert not response.is_approved
    assert repositories.user_repository.count() == 1
