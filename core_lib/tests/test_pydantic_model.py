from core_lib.repositories import User


def test_to_dict_and_parse_obj(user: User):
    assert user is not None
    assert user.dict() is not None


def test_equality(user: User):
    mock_2_user = user.copy()
    assert user == mock_2_user

    mock_3_user = user.copy(update={"given_name": "other- name"})
    assert user != mock_3_user
