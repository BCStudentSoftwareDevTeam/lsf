import pytest
from app.models.user import User
from app.models.formHistory import FormHistory
from app.models.laborStatusForm import LaborStatusForm
from app.models.term import Term
from app.models import mainDB
from peewee import DoesNotExist, JOIN

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
def test_term_model():
    """
    Beans (what we need to do):
    - create several labor status forms that belong to different terms in different years
    - create corresponding form history objects for the forms
    - write a query to select all forms
    - order the form selection using the FormHistory.order_by_term() method
    - assert that the forms are in correctly in order by date 
    """
    def createLSFandFormHistoryObj(*, termCode):
        """
        Subprocedure to create LSF and FormHistory objects for a particular termCode with dummy data.
        """
        Term.get_or_create(termCode= termCode, termName="idk");

        # [Beans] lsf object: termCode (*Term), studentSupervisee (*Student), supervisor (*Supervisor), department (*Department), jobType, WLS, POSN_TITLE, POSN_CODE 
        #                                        Alex Bryant              Brian Ramsay              CS      
        irrelevantLsfObjData = {'studentSupervisee': 'B00841417', 'supervisor': 'B00763721', 'department': 1, 'jobType': 'Primary', 'WLS': 1, 'POSN_TITLE': '', 'POSN_CODE': ''}
        lsf = LaborStatusForm.create(termCode = termCode, **irrelevantLsfObjData);
        # [Beans] form history object: formID, historyType, createdBy, createdDate, status
        #                                                            Scott Heggen
        irrelevantFhObjData = {'historyType': 'Labor Status Form', 'createdBy': 1, 'createdDate': '2024-01-30', 'status': 'Pending'}
        formHistoryObj = FormHistory.create(formID = lsf, rejectReason = "testing", **irrelevantFhObjData);
        return lsf, formHistoryObj
    
 
    with mainDB.atomic() as transaction:
        # We expect that term codes will be ordered by year with ties broken by the last two digits in this order:
        # '13', '03', '12', '02', '01', '04', '11', [default], '00'
        correctlyOrderedSeasonCodes = ['00', '99', '11', '04', '01', '02', '12', '05', '03', '13']

        # Create the forms out of order
        outOfOrderSeasonCodes = ['13', '02', '04', '00', '11', '12', '03', '99', '01', '05']
        for seasonCode in outOfOrderSeasonCodes:
            createLSFandFormHistoryObj(termCode=int(f'2025{seasonCode}'))

        newForms = FormHistory.select(FormHistory, LaborStatusForm.termCode).join(LaborStatusForm, JOIN.LEFT_OUTER).where(FormHistory.rejectReason == "testing")
        sortedForms = Term.order_by_term(newForms.objects())
        resultingTermCodes = [str(f.termCode) for f in sortedForms]
        resultingSeasonalCodes = [termCode[4:] for termCode in resultingTermCodes]
        assert resultingSeasonalCodes == correctlyOrderedSeasonCodes      

        
        transaction.rollback()

        # Test that the year has more weight in the sort than the seasonal code
        sortedTermCodes = [202311, 202302, 202313, 202400, 202412, 202403]
        unsortedTermCodes = [202302, 202403, 202313, 202311, 202400, 202412]
        for termCodes in unsortedTermCodes:
            createLSFandFormHistoryObj(termCode=int(termCodes))
        newForms = FormHistory.select(FormHistory, LaborStatusForm.termCode).join(LaborStatusForm, JOIN.LEFT_OUTER).where(FormHistory.rejectReason == "testing")
        sortedForms = Term.order_by_term(newForms.objects())
        resultingTermCodes = [f.termCode for f in sortedForms]
        assert  resultingTermCodes == sortedTermCodes
        transaction.rollback()

    

