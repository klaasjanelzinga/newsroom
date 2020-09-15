from core_lib import application_data
from core_lib.repositories import User, Feed


def mirror_side_effect(arg):
    return arg


def faked_user(faker):
    user = User(
        given_name=faker.name(),
        family_name=faker.name(),
        email=faker.email(),
        avatar_url=faker.url(),
        is_approved=faker.pybool(),
    )
    return user


def faked_feed(faker):
    return Feed(
        url=faker.url(),
        title=faker.sentence(),
        link=faker.url(),
        description=faker.sentence(),
        number_of_subscriptions=faker.pyint(),
        number_of_items=faker.pyint(),
    )


def fixture_repositories():
    repositories = application_data.repositories
    repositories.reset_mocks()
    repositories.mock_subscription_repository().upsert.side_effect = mirror_side_effect
    repositories.mock_user_repository().upsert.side_effect = mirror_side_effect
    repositories.mock_feed_repository().upsert.side_effect = mirror_side_effect
    return application_data.repositories
