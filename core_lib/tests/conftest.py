import pytest
from faker import Faker

from core_lib.repositories import User


@pytest.fixture
def faker() -> Faker:
    return Faker()


@pytest.fixture
def mock_user(faker: Faker) -> User:
    user = User(
        given_name=faker.name(),
        family_name=faker.name(),
        email=faker.email(),
        avatar_url=faker.url(),
        is_approved=faker.pybool(),
    )
    return user
