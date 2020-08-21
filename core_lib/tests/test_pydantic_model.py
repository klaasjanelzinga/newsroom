import pytest

from core_lib.user import User


def test_to_dict_and_parse_obj(mock_user: User):
    assert mock_user is not None
    assert mock_user.dict() is not None
    assert len(mock_user.dict()) == 5
    assert len(User.parse_obj(mock_user.dict()).dict()) == 5


def test_unmodifiable_objects(mock_user: User):
    with pytest.raises(TypeError):
        mock_user.email = None


def test_equality(mock_user: User):
    mock_2_user = mock_user.copy()
    assert mock_user == mock_2_user

    mock_3_user = mock_user.copy(update={"given_name": "other- name"})
    assert mock_user != mock_3_user
