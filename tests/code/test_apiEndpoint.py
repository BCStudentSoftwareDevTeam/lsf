import pytest

from app.models.formHistory import FormHistory
from app.models.laborStatusForm import LaborStatusForm
from app.models.term import Term
from app.models.supervisor import Supervisor
from app.models.user import User
from app.models import mainDB

from app import app
from app.logic.apiEndpoint import getLaborInformation

@pytest.mark.integration
def test_getLaborInformation():
    with mainDB.atomic() as transaction:
        FormHistory.update(status_id = "Approved").where(FormHistory.formHistoryID == 2).execute()

        testingSupervisor = Supervisor.create(ID = "B00000001",
                                              PIDM = 75,
                                              legal_name = "Not",
                                              LAST_NAME = "Scott",
                                              EMAIL = "None",
                                              CPO = "None",
                                              DEPT_NAME = "Computer Science")
                        
        testUser = User.create(student = None,
                               supervisor = testingSupervisor.ID,
                               username = "scottn",
                               isLaborAdmin = None,
                               isFinancialAidAdmin = None,
                               isSaasAdmin = None)
        
        with app.test_request_context():
            # Case 1: verify the LSF for Alex in demo data is returend and contains what we would expect
            response = getLaborInformation(orgCode = 2114, bNumber="B00841417")

            responseData = response.get_json()
            assert responseData['B00841417'][0]['jobType'] == "Primary"
            assert responseData['B00841417'][0]['termName'] == "AY 2020-2021"
        
        Term.create(termCode = 202100,
                    termName = "AY 2021-2022",
                    termStart = "2021-08-01",
                    termEnd = "2022-05-01",
                    primaryCutOff = "2021-09-01",
                    adjustedCutOff = "2021-09-01",
                    termState = 1,
                    isBreak = 0,
                    isSummer = 0,
                    isAcademicyear = 0, 
                    isFinalEvaluationOpen = 0,
                    isMidyearEvaluationOpen = 0)

        testLaborForm = LaborStatusForm.create(termCode_id = 202100,
                                               studentSupervisee_id = "B00841417",
                                               supervisor_id = "B12361006",
                                               department_id  = 1,
                                               jobType = "Primary",
                                               WLS = 1,
                                               POSN_TITLE = "Student Programmer",
                                               POSN_CODE = "S61407",
                                               contractHours = 160,
                                               weeklyHours   = 10,
                                               startDate = "2021-08-01",
                                               endDate = "2022-05-01",
                                               supervisorNotes = None,
                                               laborDepartmentNotes = None,
                                               studentName = "Alex Bryant"
                                               )
        
        FormHistory.create(formID_id = testLaborForm.laborStatusFormID,
                           historyType = "Labor Status Form",
                           releaseForm = None, 
                           adjustedForm = None, 
                           overloadForm = None, 
                           createdBy = testUser.userID,
                           createdDate = "2021-08-01",
                           reviewdDate = "2021-08-01",
                           reviewdBy = None, 
                           status = "Approved")
        
        with app.test_request_context():
            # Case 2: Confirm the LSF in base data and the new one created inside the test are returned and contain
            # what is expected
            response = getLaborInformation(orgCode = 2114, bNumber="B00841417")

            responseData = response.get_json()
            assert len(responseData['B00841417']) == 2
            assert responseData['B00841417'][0]['jobType'] == "Primary"
            assert responseData['B00841417'][0]['termName'] == "AY 2020-2021"
            assert responseData['B00841417'][0]['laborStart'] == "2020-04-01"
            assert responseData['B00841417'][1]['jobType'] == "Primary"
            assert responseData['B00841417'][1]['termName'] == "AY 2021-2022"
            assert responseData['B00841417'][1]['laborStart'] == "2021-08-01"

        LaborStatusForm.update(department_id = 4).where(LaborStatusForm.laborStatusFormID == testLaborForm.laborStatusFormID).execute()

        with app.test_request_context():
            # Case 3: Confirm that the LSF in base data is the only form returned since the form created in the test has
            # had its dept changed and we are only getting forms for dept 1. 
            response = getLaborInformation(orgCode = 2114, bNumber="B00841417")

            responseData = response.get_json()
            assert responseData['B00841417'][0]['jobType'] == "Primary"
            assert responseData['B00841417'][0]['termName'] == "AY 2020-2021"
            assert responseData['B00841417'][0]['laborStart'] == "2020-04-01"
            assert len(responseData['B00841417']) == 1

        transaction.rollback()
