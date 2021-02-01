import hashlib
import re
from base64 import b64decode
from os import urandom
from typing import Optional

from core_lib.application_data import repositories
from core_lib.exceptions import AuthorizationFailed, UserNameTaken, PasswordsDoNotMatch, IllegalPassword
from core_lib.repositories import User
from core_lib.utils import bytes_to_str_base64

contains_digits_re = re.compile(r"\d")
contains_caps_re = re.compile(r"[A-Z]")
contains_lower_re = re.compile(r"[a-z]")
contains_special_re = re.compile(r"[!@#$%^&*()-+ {}\[\];',.<>/?`~\\|_=]")


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


def sign_in(name: str, password: str) -> User:
    """
    Checks if the user checks out. Password is ok and the user is present if this function succeeds.

    :param name: The name of the user.
    :param password: The password of the user.
    :raises AuthorizationFailed: if the user is not found or the password does not match the records.
    """
    return verify_password(name, password)


def verify_password(name: str, password: str) -> Optional[User]:
    """ Verifies if the password is  correct. """
    user = repositories.user_repository.fetch_user_by_name(name)
    if user is None:
        raise AuthorizationFailed()
    salt = b64decode(bytes(user.password_salt, "utf-8"))
    password_hash = bytes_to_str_base64(_generate_hash(password, salt))
    if password_hash != user.password_hash:
        raise AuthorizationFailed()
    return user


def change_password(name: str, old_password: str, new_password: str, new_password_repeated: str) -> User:
    """
    Changes the password for the user with name name.

    :raises PasswordsDoNotMatch: if the passwords do not match.
    :raises IllegalPassword: if the password is not valid.
    :raises AuthorizationFailed: if the old password cannot be used to authenticate.
    """
    _validate_password(new_password)
    user = verify_password(name, old_password)
    salt = _generate_salt()

    password_hash = _generate_hash(new_password, salt)
    password_repeated_hash = _generate_hash(new_password_repeated, salt)
    if password_hash != password_repeated_hash:
        raise PasswordsDoNotMatch()

    user.password_hash = bytes_to_str_base64(password_hash)
    user.password_salt = bytes_to_str_base64(salt)
    return user


def signup(name: str, password: str, password_repeated: str) -> User:
    """
    Creates the user.

    :param name: Name of the user to create.
    :param password: The password for the user.
    :param password_repeated: The password for the user.

    :raises UserNameTaken: if the user name is already taken.
    :raises PasswordsDoNotMatch: if the passwords do not match.
    :raises IllegalPassword: if the password is not valid.
    """
    _validate_password(password)
    existing_user = repositories.user_repository.fetch_user_by_name(name)
    if existing_user is not None:
        raise UserNameTaken()

    salt = _generate_salt()
    password_hash = _generate_hash(password, salt)
    password_repeated_hash = _generate_hash(password_repeated, salt)
    if password_hash != password_repeated_hash:
        raise PasswordsDoNotMatch()
    user = User(
        name=name,
        password_hash=bytes_to_str_base64(password_hash),
        password_salt=bytes_to_str_base64(salt),
        is_approved=False,
    )
    return repositories.user_repository.upsert(user)
