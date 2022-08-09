import pytest
from app.models.user import User
from peewee import DoesNotExist

@pytest.mark.integration
def test_user_model():
    sup_user = User.get(username="heggens")
    stu_user = User.get(username="jamalie")
    both_user = User.get(username="bryantal")

    assert sup_user.firstName == "Scott"
    assert sup_user.lastName == "Heggen"
    assert sup_user.fullName == "Scott Heggen"
    assert sup_user.email == "heggens@berea.edu"

    assert stu_user.firstName == "Elaheh"
    assert stu_user.lastName == "Jamali"
    assert stu_user.fullName == "Elaheh Jamali"
    assert stu_user.email == "jamalie@berea.edu"

    assert both_user.firstName == "Alex"
    assert both_user.lastName == "Bryant"
    assert both_user.fullName == "Alex Bryant"
    assert both_user.email == "bryantal@berea.edu"
