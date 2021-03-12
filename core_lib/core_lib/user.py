from base64 import b64decode
from dataclasses import dataclass
import hashlib
from os import urandom
import random
import re
import string
from typing import List, Optional

import pyotp

from core_lib import application_data
from core_lib.exceptions import (
    AuthorizationFailed,
    BackupCodeNotValid,
    IllegalPassword,
    PasswordsDoNotMatch,
    TokenCouldNotBeVerified,
    UserNameTaken,
)
from core_lib.repositories import User
from core_lib.utils import bytes_to_str_base64

contains_digits_re = re.compile(r"\d")
contains_caps_re = re.compile(r"[A-Z]")
contains_lower_re = re.compile(r"[a-z]")
contains_special_re = re.compile(r"[!@#$%^&*()-+ {}\[\];'\",.<>/?`~\\|_=]")


def _generate_salt() -> bytes:
    return urandom(32)


def _generate_hash(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)


def _validate_password(password: str) -> None:
    """ Raises IllegalPassword if the password is not valid (too short etc). """
    if len(password) < 8:
        raise IllegalPassword("Password must be longer than 8 characters.")
    if not contains_digits_re.search(password):
        raise IllegalPassword("Password must contain digits.")
    if not contains_caps_re.search(password):
        raise IllegalPassword("Password must contain caps.")
    if not contains_lower_re.search(password):
        raise IllegalPassword("Password must contain lowers.")
    if not contains_special_re.search(password):
        raise IllegalPassword("Password must contain special characters.")


def sign_in(email_address: str, password: str) -> User:
    """
    Checks if the user checks out. Password is ok and the user is present if this function succeeds.

    :param email_address: The name of the user.
    :param password: The password of the user.
    :raises AuthorizationFailed: if the user is not found or the password does not match the records.
    """
    return verify_password(email_address, password)


def verify_password(email_address: str, password: str) -> User:
    """ Verifies if the password is  correct. """
    user = application_data.repositories.user_repository.fetch_user_by_email(email_address)
    if user is None:
        raise AuthorizationFailed()
    salt = b64decode(bytes(user.password_salt, "utf-8"))
    password_hash = bytes_to_str_base64(_generate_hash(password, salt))
    if password_hash != user.password_hash:
        raise AuthorizationFailed()
    return user


def change_password(email_address: str, current_password: str, new_password: str, new_password_repeated: str) -> User:
    """
    Changes the password for the user with name name.

    :raises PasswordsDoNotMatch: if the passwords do not match.
    :raises IllegalPassword: if the password is not valid.
    :raises AuthorizationFailed: if the old password cannot be used to authenticate.
    """
    _validate_password(new_password)
    user = verify_password(email_address, current_password)
    salt = _generate_salt()

    password_hash = _generate_hash(new_password, salt)
    password_repeated_hash = _generate_hash(new_password_repeated, salt)
    if password_hash != password_repeated_hash:
        raise PasswordsDoNotMatch("Passwords do not match")

    user.password_hash = bytes_to_str_base64(password_hash)
    user.password_salt = bytes_to_str_base64(salt)
    return user


def signup(email_address: str, password: str, password_repeated: str) -> User:
    """
    Creates the user.

    :param email_address: Name of the user to create.
    :param password: The password for the user.
    :param password_repeated: The password for the user.

    :raises UserNameTaken: if the user name is already taken.
    :raises PasswordsDoNotMatch: if the passwords do not match.
    :raises IllegalPassword: if the password is not valid.
    """
    _validate_password(password)
    existing_user = application_data.repositories.user_repository.fetch_user_by_email(email_address)
    if existing_user is not None:
        raise UserNameTaken()

    salt = _generate_salt()
    password_hash = _generate_hash(password, salt)
    password_repeated_hash = _generate_hash(password_repeated, salt)
    if password_hash != password_repeated_hash:
        raise PasswordsDoNotMatch("Passwords do not match")
    user = User(
        email_address=email_address,
        password_hash=bytes_to_str_base64(password_hash),
        password_salt=bytes_to_str_base64(salt),
        is_approved=False,
    )
    return application_data.repositories.user_repository.upsert(user)


def update_user_profile(
    user: User, display_name: Optional[str], avatar_image: Optional[str], avatar_action: str
) -> User:
    """ Update profile and avatar. Return the updated user. """
    user.display_name = display_name
    if avatar_action == "delete":
        application_data.repositories.user_repository.update_avatar(user, None)
    if avatar_image is not None:
        application_data.repositories.user_repository.update_avatar(user, avatar_image)
    return application_data.repositories.user_repository.upsert(user)


def avatar_image_for_user(user: User) -> Optional[str]:
    avatar = application_data.repositories.user_repository.fetch_avatar_for_user(user)
    if avatar is None:
        return None
    return avatar.image


def _random_string(length: int) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


@dataclass
class OtpRegistrationResult:
    generated_secret: str
    backup_codes: List[str]
    uri: str
    user: User


def start_registration_new_otp_for(user: User) -> OtpRegistrationResult:
    """ Start OTP registration process for the TOTP, returning the secret and a uri for generating a qr-code."""
    generated_secret = pyotp.random_base32()

    user.pending_otp_hash = generated_secret
    user.pending_backup_codes = [_random_string(16) for _ in range(6)]
    uri = pyotp.totp.TOTP(generated_secret).provisioning_uri(
        name=user.display_name or user.email_address, issuer_name="Newsroom"
    )

    application_data.repositories.user_repository.upsert(user)
    return OtpRegistrationResult(
        generated_secret=generated_secret, uri=uri, user=user, backup_codes=user.pending_backup_codes
    )


def disable_otp_for(user: User) -> User:
    """ Disables the OTP for the user. """
    user.pending_otp_hash = None
    user.pending_backup_codes = []
    user.otp_hash = None
    user.otp_backup_codes = []

    application_data.repositories.user_repository.upsert(user)
    return user


def confirm_otp_for(user: User, totp_value: str) -> User:
    """ Confirms the generated secret for the user by submitting a totp-value. """
    if user.pending_otp_hash is None:
        raise TokenCouldNotBeVerified("Token could not be verified")

    totp = pyotp.TOTP(user.pending_otp_hash)
    if not totp.verify(totp_value):
        raise TokenCouldNotBeVerified("Token could not be verified")

    user.otp_hash = user.pending_otp_hash
    user.otp_backup_codes = user.pending_backup_codes
    user.pending_otp_hash = None
    user.pending_backup_codes = []
    user = application_data.repositories.user_repository.upsert(user)
    return user


def totp_verification_for(user: User, totp_value: str) -> User:
    """ Verifies the totp value for the user. """
    if user.otp_hash is None:
        raise TokenCouldNotBeVerified("Token could not be verified")

    totp = pyotp.TOTP(user.otp_hash)
    if not totp.verify(totp_value, valid_window=5):
        raise TokenCouldNotBeVerified("Token could not be verified")
    return user


def use_backup_code_for(user: User, backup_code: str) -> User:
    """ Uses the backup code for the user. """
    if backup_code not in user.otp_backup_codes:
        raise BackupCodeNotValid()
    user.otp_backup_codes = [code for code in user.otp_backup_codes if code != backup_code]
    return application_data.repositories.user_repository.upsert(user)
