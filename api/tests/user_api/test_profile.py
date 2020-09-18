from unittest.mock import patch, Mock

import pytest
from faker import Faker

from api.user_api import update_user_profile, UpdateUserProfileRequest
from core_lib.application_data import Repositories
from core_lib.repositories import User
from tests.conftest import authorization_for


@pytest.mark.asyncio
@patch("api.user_api.security")
async def test_change_profile(security_mock: Mock, faker: Faker, user: User, repositories: Repositories):
    with authorization_for(security_mock, user):
        request = UpdateUserProfileRequest(given_name=faker.name(), family_name=faker.name())
        response = await update_user_profile(updated_user_request=request, authorization=faker.word())

        assert response.email == user.email
        assert response.given_name == request.given_name
        assert response.family_name == request.family_name
        assert response.subscribed_to == user.subscribed_to
        repositories.mock_user_repository().upsert.assert_called_once()
