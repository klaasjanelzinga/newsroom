import random

import pyotp
import pytest
from faker import Faker
from fastapi import HTTPException

from api.feed_api import get_all_feeds
from api.user_api import (
    start_totp_registration,
    confirm_totp,
    TOTPVerificationRequest,
    UserSignInRequest,
    sign_in_user,
    SignInState,
    totp_verification,
    disable_totp,
    use_totp_backup_code,
    UseTOTPBackupRequest,
)
from core_lib.repositories import User
from tests.mock_repositories import MockRepositories


@pytest.mark.asyncio
async def test_enable_totp(
    repositories: MockRepositories, faker: Faker, user: User, user_password: str, user_bearer_token
):
    # Sign does not need OTP
    user_sign_in_request = UserSignInRequest(email_address=user.email_address, password=user_password)
    response = await sign_in_user(user_sign_in_request)
    assert response.sign_in_state == SignInState.SIGNED_IN
    assert response.token is not None

    # API calls should work with this username / password token.
    await get_all_feeds(authorization=f"Bearer {response.token}")

    # Start registration for TOTP ------------------------------------------------------------
    totp_response = await start_totp_registration(authorization=user_bearer_token)
    assert len(totp_response.backup_codes) > 5
    assert totp_response.generated_secret is not None

    user = repositories.user_repository.fetch_user_by_email(user.email_address)

    assert user.pending_backup_codes is not None
    assert user.pending_otp_hash is not None

    # Confirm with TOTP code ------------------------------------------------------------
    verification_code = pyotp.TOTP(totp_response.generated_secret).now()
    confirmation_result = await confirm_totp(TOTPVerificationRequest(totp_value=verification_code), user_bearer_token)
    assert confirmation_result.otp_confirmed

    assert user.pending_backup_codes == []
    assert user.pending_otp_hash is None
    assert user.otp_backup_codes is not None
    assert user.otp_hash is not None

    # Sign needs otp now
    user_sign_in_request = UserSignInRequest(email_address=user.email_address, password=user_password)
    response = await sign_in_user(user_sign_in_request)
    assert response.sign_in_state == SignInState.REQUIRES_OTP
    assert response.token is not None

    # API calls no longer work with tokens not verified with otp
    with pytest.raises(HTTPException) as http_exception:
        await get_all_feeds(authorization=f"Bearer {response.token}")
    assert http_exception.value.status_code == 401

    with pytest.raises(HTTPException) as http_exception:
        await get_all_feeds(authorization=user_bearer_token)
    assert http_exception.value.status_code == 401

    # sign in with OTP and API calls work again
    response = await totp_verification(
        TOTPVerificationRequest(totp_value=verification_code), authorization=f"Bearer {response.token}"
    )
    assert response.token is not None
    verified_token = response.token
    response = await get_all_feeds(authorization=f"Bearer {verified_token}")
    assert response is not None

    # disable OTP, API should work again with old tokens (non-verified)
    await disable_totp(authorization=f"Bearer {verified_token}")
    await get_all_feeds(authorization=user_bearer_token)


@pytest.mark.asyncio
async def test_backup_codes(repositories: MockRepositories, user: User, user_password: str, user_bearer_token: str):
    # Start registration for TOTP
    totp_response = await start_totp_registration(authorization=user_bearer_token)
    assert len(totp_response.backup_codes) > 5
    backup_codes = totp_response.backup_codes

    # confirm TOTP
    verification_code = pyotp.TOTP(totp_response.generated_secret).now()
    confirmation_result = await confirm_totp(TOTPVerificationRequest(totp_value=verification_code), user_bearer_token)
    assert confirmation_result.otp_confirmed

    # sign in with a backup code
    backup_code = random.choice(backup_codes)
    user_sign_in_request = UserSignInRequest(email_address=user.email_address, password=user_password)
    response = await sign_in_user(user_sign_in_request)
    response = await use_totp_backup_code(
        UseTOTPBackupRequest(totp_backup_code=backup_code), authorization=f"Bearer {response.token}"
    )
    assert response is not None

    # API calls should work with this token, verified with the backup code.
    await get_all_feeds(authorization=f"Bearer {response.token}")

    # The backup code should no longer be there.
    assert backup_code not in user.otp_backup_codes
    with pytest.raises(HTTPException) as http_exception:
        await use_totp_backup_code(
            UseTOTPBackupRequest(totp_backup_code=backup_code), authorization=f"Bearer {response.token}"
        )
    assert http_exception.value.status_code == 401
