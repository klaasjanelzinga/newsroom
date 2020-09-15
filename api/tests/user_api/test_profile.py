from unittest.mock import patch, AsyncMock, Mock

import pytest

from api.user_api import fetch_user
from core_lib.repositories import User


@pytest.mark.asyncio
@patch("api.user_api.security")
async def test_fetch_user(security_mock: Mock, user: User):
    security_mock.get_approved_user = AsyncMock()
    security_mock.get_approved_user.return_value = user

    result = await fetch_user("dummy-header")
    assert result.email == user.email
    assert result.given_name == user.given_name
    assert result.family_name == user.family_name
    assert result.user_id == user.user_id
