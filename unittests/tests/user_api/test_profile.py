from unittest.mock import patch, Mock

import pytest
from faker import Faker

from api.user_api import update_user_profile, UpdateUserProfileRequest
from core_lib.repositories import User
from tests.conftest import authorization_for
from tests.mock_repositories import MockRepositories


@pytest.mark.asyncio
@patch("api.user_api.security")
async def test_change_profile(security_mock: Mock, faker: Faker, user: User, repositories: MockRepositories):
    with authorization_for(security_mock, user, repositories):
        request = UpdateUserProfileRequest(given_name=faker.name(), family_name=faker.name())
        response = await update_user_profile(updated_user_request=request, authorization=faker.word())

        assert response.email == user.email
        assert response.given_name == request.given_name
        assert response.family_name == request.family_name
        assert response.subscribed_to == user.subscribed_to

        assert repositories.user_repository.count() == 1
        assert repositories.user_repository.fetch_user_by_email(response.email).family_name == request.family_name
        assert repositories.user_repository.fetch_user_by_email(response.email).given_name == request.given_name
