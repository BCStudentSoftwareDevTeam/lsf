import pytest
from app.controllers.main_routes.studentLaborEvaluation import sle
from app import app
from flask_wtf.csrf import CSRFProtect
import pytest
from app.models import mainDB
from app.models.laborStatusForm import LaborStatusForm
from app.models.department import Department
from app.models.term import Term
from app.models.formHistory import FormHistory
from app.models.student import Student
from app.models.supervisor import Supervisor
from app.models.user import User
from app.logic.userInsertFunctions import createLaborStatusForm
from app.models.studentLaborEvaluation import StudentLaborEvaluation
import json


@pytest.mark.integration
def testCreateStudentEval():
    with mainDB.atomic() as transaction:
        testingDept = Department.create(DEPT_NAME="Computer Science", ACCOUNT="6740", ORG="2114")
        testingTerm = (Term.create(termCode = 200000,
                        termName = "Testing Term",
                        termStart="2022-08-01", termEnd="2022-05-01",
                        primaryCutOff="2022-09-01", adjustedCutOff="2022-09-01",
                        termState=1,
                        isBreak=0,
                        isSummer=0,
                        isAcademicYear=0,
                        isFinalEvaluationOpen=1))

        testingStudent =  (Student.create(
                ID="B00000002",
                legal_name="Tyler",
                LAST_NAME="Parton",
                STU_EMAIL="partont@whatever.edu",
                STU_CPO="Unknown"
                ))
        testingSupervisor = Supervisor.create(ID = "B00000001",
                               PIDM = 75,
                               legal_name = "Not",
                               LAST_NAME = "Scott",
                               EMAIL = "None",
                               CPO = "None",
                               DEPT_NAME = "Computer Science")


        testingLSF = LaborStatusForm.create(studentName = "Tyler Parton",
                                            termCode = 200000,
                                            studentSupervisee = "B00000002",
                                            supervisor = "B00000001",
                                            department = testingDept.departmentID,
                                            jobType = "Primary",
                                            WLS = "1",
                                            POSN_TITLE = "Student Programmer",
                                            POSN_CODE = "S61407")

        testUser = User.create(student = None,
                                         supervisor = testingSupervisor.ID,
                                         username = "scottn",
                                         isLaborAdmin = None,
                                         isFinancialAidAdmin = None,
                                         isSaasAdmin = None)


        testingFormHistory = (FormHistory.create(formID = testingLSF.laborStatusFormID,
                                               historyType = "Labor Status Form",
                                               releaseForm = None,
                                               adjustedForm = None,
                                               overloadForm = None,
                                               createdBy = testUser.userID,
                                               createdDate = "2020-04-14",
                                               reviewedDate = "2020-04-14",
                                               reviewedBy = None,
                                               status = "Approved"))

        testCreation = {"isSubmitted": True,
                        "submit_as_final": True,
                        "attendance": 15,
                        "accountability": 7,
                        "teamwork": 7,
                        "initiative": 7,
                        "respect": 7,
                        "learning": 15,
                        "jobSpecific": 15,
                        "attendanceComments": " ",
                        "teamworkComments": " ",
                        "initiativeComments": " ",
                        "respectComments": " ",
                        "accountabilityComments": " ",
                        "learningComments": " ",
                        "jobSpecificComments": " ", 
                        "transcriptComments": " "}

        testReset = {"resetConfirmation": True}

        with app.test_request_context( "/sle", method="POST", data=testCreation):
                app.config['WTF_CSRF_ENABLED'] = False
                app.config['show_queries'] = False
                createSLEform = sle(testingLSF.laborStatusFormID)
                assert StudentLaborEvaluation.get_or_none(StudentLaborEvaluation.formHistoryID == testingFormHistory.formHistoryID) != None

        with app.test_request_context( "/sle", method="POST", data=testReset):
                app.config['WTF_CSRF_ENABLED'] = False
                app.config['show_queries'] = False
                createSLEform = sle(testingLSF.laborStatusFormID)
                assert StudentLaborEvaluation.get_or_none(StudentLaborEvaluation.formHistoryID == testingFormHistory.formHistoryID) == None
                transaction.rollback()
