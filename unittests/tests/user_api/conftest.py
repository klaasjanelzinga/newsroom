import pytest
from faker import Faker

from core_lib.repositories import User
from core_lib.user import signup


@pytest.fixture
def user_name(faker: Faker) -> str:
    return faker.email()


@pytest.fixture
def user_password(faker: Faker) -> str:
    return faker.password(length=16, special_chars=True, digits=True, upper_case=True, lower_case=True)


@pytest.fixture
def signed_up_user(user_name: str, user_password: str) -> User:
    user = signup(name=user_name, password_repeated=user_password, password=user_password)
    return user
