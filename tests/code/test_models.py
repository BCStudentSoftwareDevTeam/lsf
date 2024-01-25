import pytest
from app.models.user import User
from app.models.formHistory import FormHistory
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


@pytest.mark.integration
def test_form_history_model():
     """
     Beans (what we need to do):
     - create several labor status forms that belong to different terms in different years
     - create corresponding form history objects for the forms
     - write a query to select all forms
     - order the form selection using the FormHistory.order_by_date() method
     - assert that the forms are in correctly in order by date 
     """
    return
    # [Beans] each form history object needs: formID, historyType, createdBy, createdDate, status
    formHistories = FormHistory.create(   formID       = lsf.laborStatusFormID,
                                           historyType  = "Labor Adjustment Form",
                                           adjustedForm = adjustedforms.adjustedFormID,
                                           createdBy    = currentUser,
                                           createdDate  = date.today(),
                                           status       = "Pending")

