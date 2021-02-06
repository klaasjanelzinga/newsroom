import pytest
from faker import Faker

from core_lib.repositories import User
from core_lib.user import signup
from tests.mock_repositories import MockRepositories


@pytest.fixture
def user_email_address(faker: Faker) -> str:
    return faker.email()


@pytest.fixture
def user_password(faker: Faker) -> str:
    return faker.password(length=16, special_chars=True, digits=True, upper_case=True, lower_case=True)


@pytest.fixture
def signed_up_user(user_email_address, user_password: str) -> User:
    user = signup(email_address=user_email_address, password_repeated=user_password, password=user_password)
    return user


@pytest.fixture
def approved_up_user(repositories: MockRepositories, user_email_address, user_password: str) -> User:
    user = signup(email_address=user_email_address, password_repeated=user_password, password=user_password)
    user.is_approved = True
    repositories.user_repository.upsert(user)
    return user
