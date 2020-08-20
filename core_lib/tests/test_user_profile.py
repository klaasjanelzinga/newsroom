from core_lib.user_profile import UserProfile


def test_create():
    user_profile = UserProfile(
        given_name="test", email="", family_name="", avatar_url="", is_approved=False
    )
    assert user_profile is not None
