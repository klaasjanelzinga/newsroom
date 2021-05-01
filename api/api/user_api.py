import enum
import logging
from typing import List, Optional

from fastapi import APIRouter, Header, HTTPException
from pydantic.main import BaseModel
from starlette import status

from api.api_application_data import security
from api.api_utils import ErrorMessage
from api.security import TokenVerifier
from core_lib.application_data import repositories
from core_lib.exceptions import AuthorizationException, IllegalPassword, PasswordsDoNotMatch, TokenCouldNotBeVerified
from core_lib.repositories import User
from core_lib.user import (
    avatar_image_for_user,
    change_password,
    confirm_otp_for,
    disable_otp_for,
    sign_in,
    signup,
    start_registration_new_otp_for,
    totp_verification_for,
    update_user_profile,
    use_backup_code_for,
)

user_router = APIRouter()
logger = logging.getLogger(__name__)


class UserResponse(BaseModel):
    email_address: str
    display_name: Optional[str]
    is_approved: bool
    totp_enabled: bool


class UserSignUpRequest(BaseModel):
    email_address: str
    password: str
    password_repeated: str


class UserSignInRequest(BaseModel):
    email_address: str
    password: str


class SignInState(enum.Enum):
    REQUIRES_OTP = "REQUIRES_OTP"
    SIGNED_IN = "SIGNED_IN"


class UserSignInResponse(BaseModel):
    sign_in_state: SignInState
    user: UserResponse
    token: Optional[str]


class TOTPVerificationRequest(BaseModel):
    totp_value: str


class ConfirmTotpResponse(BaseModel):
    otp_confirmed: bool


class UserChangePasswordRequest(BaseModel):
    email_address: str
    current_password: str
    new_password: str
    new_password_repeated: str


class UserChangePasswordResponse(BaseModel):
    success: bool
    message: Optional[str]


class UpdateUserProfileRequest(BaseModel):
    display_name: Optional[str]
    avatar_image: Optional[str]
    avatar_action: str


class UserAvatarResponse(BaseModel):
    avatar_image: Optional[str]


class OTPRegistrationResponse(BaseModel):
    generated_secret: str
    uri: str
    backup_codes: List[str]


class UseTOTPBackupRequest(BaseModel):
    totp_backup_code: str


def user_to_user_response(user: User) -> UserResponse:
    return UserResponse(
        email_address=user.email_address,
        display_name=user.display_name,
        is_approved=user.is_approved,
        totp_enabled=user.otp_hash is not None,
    )


@user_router.post(
    "/user/signup",
    tags=["user"],
    response_model=UserSignInResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorMessage},
    },
)
async def sign_up_user(user_sign_up_request: UserSignUpRequest) -> UserSignInResponse:
    """
    Sign up the user.
    """
    try:
        user = signup(
            email_address=user_sign_up_request.email_address,
            password=user_sign_up_request.password,
            password_repeated=user_sign_up_request.password_repeated,
        )
        token = TokenVerifier.create_token(user)
        return UserSignInResponse(
            token=token,
            sign_in_state=SignInState.SIGNED_IN,
            user=user_to_user_response(user),
        )
    except AuthorizationException as authorization_exception:
        raise HTTPException(status_code=401, detail=authorization_exception.__str__()) from authorization_exception


@user_router.post(
    "/user/change_password",
    tags=["user"],
    responses={
        status.HTTP_200_OK: {"model": UserChangePasswordResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorMessage},
    },
)
async def change_password_user(
    user_change_password_request: UserChangePasswordRequest, authorization: Optional[str] = Header(None)
) -> UserChangePasswordResponse:
    """
    Change the password for the user.
    """
    try:
        await security.get_approved_user(authorization)
        change_password(
            email_address=user_change_password_request.email_address,
            current_password=user_change_password_request.current_password,
            new_password=user_change_password_request.new_password,
            new_password_repeated=user_change_password_request.new_password_repeated,
        )
        return UserChangePasswordResponse(success=True)
    except IllegalPassword as illegal_password:
        return UserChangePasswordResponse(success=False, message=illegal_password.__str__())
    except PasswordsDoNotMatch as no_match:
        return UserChangePasswordResponse(success=False, message=no_match.__str__())
    except AuthorizationException as authorization_exception:
        raise HTTPException(status_code=401, detail=authorization_exception.__str__()) from authorization_exception


@user_router.post(
    "/user/signin",
    tags=["user"],
    response_model=UserSignInResponse,
    responses={
        status.HTTP_200_OK: {
            "model": User,
            "description": "The user is logged in.",
        },
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorMessage},
    },
)
async def sign_in_user(user_sign_in_request: UserSignInRequest) -> UserSignInResponse:
    try:
        user = sign_in(email_address=user_sign_in_request.email_address, password=user_sign_in_request.password)
        token = TokenVerifier.create_token(user, token_verified=False)
        return UserSignInResponse(
            token=token,
            sign_in_state=SignInState.SIGNED_IN if user.otp_hash is None else SignInState.REQUIRES_OTP,
            user=user_to_user_response(user),
        )
    except AuthorizationException as authorization_exception:
        raise HTTPException(status_code=401) from authorization_exception


@user_router.post(
    "/user/update-profile",
    tags=["user"],
    response_model=UserResponse,
    responses={
        status.HTTP_200_OK: {
            "model": User,
            "description": "The user profile is updated.",
        },
    },
)
async def update_profile(
    update_profile_request: UpdateUserProfileRequest, authorization: Optional[str] = Header(None)
) -> UserResponse:
    try:
        user = await security.get_approved_user(authorization)
        user = update_user_profile(
            user,
            update_profile_request.display_name,
            avatar_image=update_profile_request.avatar_image,
            avatar_action=update_profile_request.avatar_action,
        )
        return user_to_user_response(user)
    except AuthorizationException as authorization_exception:
        raise HTTPException(status_code=401) from authorization_exception


@user_router.get(
    "/user/avatar",
    tags=["user"],
    response_model=UserAvatarResponse,
)
async def fetch_avatar_image(authorization: Optional[str] = Header(None)) -> UserAvatarResponse:
    try:
        user = await security.get_approved_user(authorization)
        return UserAvatarResponse(avatar_image=avatar_image_for_user(user))
    except AuthorizationException as authorization_exception:
        raise HTTPException(status_code=401) from authorization_exception


@user_router.post(
    "/user/start-totp-registration",
    tags=["User"],
    response_model=OTPRegistrationResponse,
)
async def start_totp_registration(authorization: Optional[str] = Header(None)) -> OTPRegistrationResponse:
    try:
        user = await security.get_approved_user(authorization)
        otp_result = start_registration_new_otp_for(user)
        return OTPRegistrationResponse(
            generated_secret=otp_result.generated_secret,
            uri=otp_result.uri,
            backup_codes=otp_result.backup_codes,
        )
    except AuthorizationException as authorization_exception:
        raise HTTPException(status_code=401) from authorization_exception


@user_router.post(
    "/user/totp-verification",
    tags=["User"],
    response_model=UserSignInResponse,
)
async def totp_verification(
    totp_verification_request: TOTPVerificationRequest, authorization: Optional[str] = Header(None)
) -> UserSignInResponse:
    try:
        user = await security.get_approved_user(authorization, check_totp=False)
        user = totp_verification_for(user, totp_verification_request.totp_value)
        token = TokenVerifier.create_token(user, token_verified=True)
        return UserSignInResponse(
            token=token,
            sign_in_state=SignInState.SIGNED_IN,
            user=user_to_user_response(user),
        )
    except AuthorizationException as authorization_exception:
        raise HTTPException(status_code=401) from authorization_exception


@user_router.post(
    "/user/confirm-totp",
    tags=["User"],
    response_model=ConfirmTotpResponse,
)
async def confirm_totp(
    otp_login_request: TOTPVerificationRequest, authorization: Optional[str] = Header(None)
) -> ConfirmTotpResponse:
    try:
        user = await security.get_approved_user(authorization)
        confirm_otp_for(user, otp_login_request.totp_value)
        return ConfirmTotpResponse(otp_confirmed=True)
    except TokenCouldNotBeVerified:
        return ConfirmTotpResponse(otp_confirmed=False)
    except AuthorizationException as authorization_exception:
        raise HTTPException(status_code=401) from authorization_exception


@user_router.post(
    "/user/disable-totp",
    tags=["User"],
    response_model=UserResponse,
)
async def disable_totp(authorization: Optional[str] = Header(None)) -> UserResponse:
    try:
        user = await security.get_approved_user(authorization)
        user = disable_otp_for(user)
        return user_to_user_response(user)
    except AuthorizationException as authorization_exception:
        raise HTTPException(status_code=401) from authorization_exception


@user_router.post(
    "/user/use-totp-backup-code",
    tags=["User"],
    response_model=UserSignInResponse,
)
async def use_totp_backup_code(
    backup_request: UseTOTPBackupRequest, authorization: Optional[str] = Header(None)
) -> UserSignInResponse:
    try:
        user = await security.get_approved_user(authorization, check_totp=False)
        user = use_backup_code_for(user, backup_request.totp_backup_code)
        token = TokenVerifier.create_token(user, token_verified=True)
        return UserSignInResponse(
            token=token,
            sign_in_state=SignInState.SIGNED_IN,
            user=user_to_user_response(user),
        )
    except AuthorizationException as authorization_exception:
        raise HTTPException(status_code=401) from authorization_exception
