import pytest
from faker import Faker

from api.security import TokenVerifier
from core_lib.repositories import User
from core_lib.user import signup, _generate_hash, _generate_salt
from core_lib.utils import bytes_to_str_base64
from tests.mock_repositories import MockRepositories


@pytest.fixture
def signed_up_user_email_address(faker: Faker) -> str:
    return faker.email()


@pytest.fixture
def signed_up_user_password(faker: Faker) -> str:
    return faker.password(length=16, special_chars=True, digits=True, upper_case=True, lower_case=True)


@pytest.fixture
def signed_up_user_password(faker: Faker) -> str:
    return faker.password(length=16, special_chars=True, digits=True, upper_case=True, lower_case=True)


@pytest.fixture
def signed_up_user_password_salt() -> bytes:
    return _generate_salt()


@pytest.fixture
def signed_up_bearer_token(faker: Faker, signed_up_user: User) -> str:
    return f"Bearer {TokenVerifier.create_token(signed_up_user)}"


@pytest.fixture
def signed_up_user_password_hash(signed_up_user_password: str, signed_up_user_password_salt: bytes) -> bytes:
    return _generate_hash(signed_up_user_password, signed_up_user_password_salt)


@pytest.fixture
def signed_up_user(
    faker: Faker,
    repositories: MockRepositories,
    signed_up_user_email_address: str,
    signed_up_user_password_hash: bytes,
    signed_up_user_password_salt: bytes,
) -> User:
    user = User(
        email_address=signed_up_user_email_address,
        display_name=faker.name(),
        password_hash=bytes_to_str_base64(signed_up_user_password_hash),
        password_salt=bytes_to_str_base64(signed_up_user_password_salt),
        is_approved=False,
    )
    user = repositories.user_repository.upsert(user)
    return user


@pytest.fixture
def approved_up_user_email_address(faker: Faker) -> str:
    return faker.email()


@pytest.fixture
def approved_up_user_password(faker: Faker) -> str:
    return faker.password(length=16, special_chars=True, digits=True, upper_case=True, lower_case=True)


@pytest.fixture
def approved_up_user_password(faker: Faker) -> str:
    return faker.password(length=16, special_chars=True, digits=True, upper_case=True, lower_case=True)


@pytest.fixture
def approved_up_user_password_salt() -> bytes:
    return _generate_salt()


@pytest.fixture
def approved_up_user_password_hash(approved_up_user_password: str, approved_up_user_password_salt: bytes) -> bytes:
    return _generate_hash(approved_up_user_password, approved_up_user_password_salt)


@pytest.fixture
def approved_up_user(
    faker: Faker,
    repositories: MockRepositories,
    approved_up_user_email_address: str,
    approved_up_user_password_hash: bytes,
    approved_up_user_password_salt: bytes,
) -> User:
    user = User(
        email_address=approved_up_user_email_address,
        display_name=faker.name(),
        password_hash=bytes_to_str_base64(approved_up_user_password_hash),
        password_salt=bytes_to_str_base64(approved_up_user_password_salt),
        is_approved=True,
    )
    user = repositories.user_repository.upsert(user)
    return user


@pytest.fixture
def approved_up_bearer_token(faker: Faker, approved_up_user: User) -> str:
    return f"Bearer {TokenVerifier.create_token(approved_up_user)}"
