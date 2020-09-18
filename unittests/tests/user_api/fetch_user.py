from unittest.mock import patch, Mock

import pytest
from faker import Faker

from api.user_api import fetch_user
from core_lib.repositories import User
from tests.conftest import authorization_for


@pytest.mark.asyncio
@patch("api.user_api.security")
async def test_fetch_user(security_mock: Mock, faker: Faker, user: User):
    with authorization_for(security_mock, user):

        result = await fetch_user(faker.word())
        assert result.email == user.email
        assert result.given_name == user.given_name
        assert result.family_name == user.family_name
        assert result.user_id == user.user_id
