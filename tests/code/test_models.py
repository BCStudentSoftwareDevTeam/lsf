import pytest
from app.models.user import User
from app.models.formHistory import FormHistory
from app.models.laborStatusForm import LaborStatusForm
from app.models import mainDB
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
    def createLSFandFormHistoryObj(*, termCode):
        """
        Subprocedure to create LSF and FormHistory objects for a particular termCode with dummy data.
        """
        # [Beans] lsf object: termCode (*Term), studentSupervisee (*Student), supervisor (*Supervisor), department (*Department), jobType, WLS, POSN_TITLE, POSN_CODE 
        #                                        Alex Bryant              Brian Ramsay              CS      
        irrelevantLsfObjData = {'studentSupervisee': 'B00841417', 'supervisor': 'B00763721', 'department': 1, 'jobType': 'Primary', 'WLS': 1, 'POSN_TITLE': '', 'POSN_CODE': ''}
        lsf = LaborStatusForm.create(termCode = termCode, **irrelevantLsfObjData)
        # [Beans] form history object: formID, historyType, createdBy, createdDate, status
        #                                                            Scott Heggen
        irrelevantFhObjData = {'historyType': 'Labor Status Form', 'createdBy': 1, 'createdDate': '2024-01-30', 'status': 'Pending'}
        formHistoryObj = FormHistory.create(formID = lsf, **irrelevantFhObjData)
        return lsf, formHistoryObj
    
    
    with mainDB.atomic() as transaction:
        # We expect that term codes will be ordered by year with ties broken by the last two digits in this order:
        # 00, default, 11, 04, 01, 02, 12, 05, 03, 13

        # Test that ties are broken correctly

        # Create the forms out of order
        outOfOrderSemesterCodes = ['13', '02', '04', '00', '11', '12', '03', '99', '01', '05']
        for semesterCode in outOfOrderSemesterCodes:
            createLSFandFormHistoryObj(termCode=int(f'2025{semesterCode}'))


        transaction.rollback()
    
    
    

