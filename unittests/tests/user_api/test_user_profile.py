import pytest
from faker import Faker
from fastapi import HTTPException

from api.user_api import update_profile, UpdateUserProfileRequest
from core_lib.repositories import User
from tests.mock_repositories import MockRepositories


@pytest.mark.asyncio
async def test_change_display_name(repositories: MockRepositories, faker: Faker, user: User, bearer_token: str):
    with pytest.raises(HTTPException) as http_exception:
        update_profile_request = UpdateUserProfileRequest(display_name="new name")
        await update_profile(update_profile_request, f"{bearer_token}-wrong")
    assert http_exception.value.status_code == 401

    new_name = faker.name()
    update_profile_request = UpdateUserProfileRequest(display_name=new_name)
    response = await update_profile(update_profile_request, bearer_token)
    assert response.display_name == new_name
    assert response.email_address == user.email_address
    assert response.is_approved == user.is_approved
    assert user.display_name == new_name
    assert repositories.user_repository.fetch_user_by_email(user.email_address).display_name == new_name
