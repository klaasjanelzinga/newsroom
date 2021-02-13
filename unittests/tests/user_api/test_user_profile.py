import pytest
from faker import Faker
from fastapi import HTTPException

from api.user_api import update_profile, UpdateUserProfileRequest, fetch_avatar_image
from core_lib.repositories import User
from tests.mock_repositories import MockRepositories


@pytest.mark.asyncio
async def test_change_display_name(repositories: MockRepositories, faker: Faker, user: User, user_bearer_token):
    new_name = faker.name()
    new_avatar = faker.paragraph()
    update_profile_request = UpdateUserProfileRequest(
        display_name=new_name, avatar_image=new_avatar, avatar_action="keep"
    )
    response = await update_profile(update_profile_request, user_bearer_token)
    assert response.display_name == new_name
    assert response.email_address == user.email_address
    assert response.is_approved == user.is_approved
    assert user.display_name == new_name
    assert repositories.user_repository.fetch_user_by_email(user.email_address).display_name == new_name

    avatar = await fetch_avatar_image(user_bearer_token)
    assert avatar.avatar_image == new_avatar

    new_name = None
    new_avatar = None
    update_profile_request = UpdateUserProfileRequest(
        display_name=new_name, avatar_image=new_avatar, avatar_action="delete"
    )
    response = await update_profile(update_profile_request, user_bearer_token)
    assert response.display_name == new_name
    avatar = await fetch_avatar_image(user_bearer_token)
    assert avatar.avatar_image == new_avatar


@pytest.mark.asyncio
async def test_change_display_name_authorization(
    repositories: MockRepositories, faker: Faker, user: User, user_bearer_token
):
    with pytest.raises(HTTPException) as http_exception:
        update_profile_request = UpdateUserProfileRequest(display_name="new name", avatar_action="keep")
        await update_profile(update_profile_request, f"{user_bearer_token}-wrong")
    assert http_exception.value.status_code == 401


@pytest.mark.asyncio
async def test_keep_avatar_but_dont_send(repositories: MockRepositories, faker: Faker, user: User, user_bearer_token):
    new_name = faker.name()
    new_avatar = faker.paragraph()
    update_profile_request = UpdateUserProfileRequest(
        display_name=new_name, avatar_image=new_avatar, avatar_action="keep"
    )
    await update_profile(update_profile_request, user_bearer_token)

    avatar = await fetch_avatar_image(user_bearer_token)
    assert avatar.avatar_image == new_avatar

    update_profile_request = UpdateUserProfileRequest(display_name=new_name, avatar_image=None, avatar_action="keep")
    await update_profile(update_profile_request, user_bearer_token)

    avatar = await fetch_avatar_image(user_bearer_token)
    assert avatar.avatar_image == new_avatar
