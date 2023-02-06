import pytest
from app.controllers.main_routes.studentLaborEvaluation import sle
from app import app
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
        testingDept = Department.create(DEPT_NAME="Testing Department", ACCOUNT="6740", ORG="2114")
        testingTerm = Term.create(termCode = 200000, termName = "Testing Term")
        testingStudent =  (Student.create(
                ID="B00000002",
                FIRST_NAME="Tyler",
                LAST_NAME="Parton",
                STU_EMAIL="partont@whatever.edu",
                STU_CPO="Unknown"
                ))
        testingSupervisor = Supervisor.create(ID = "B00000001",
                               PIDM = 75,
                               FIRST_NAME = "Not",
                               LAST_NAME = "Scott",
                               EMAIL = "None",
                               CPO = "None",
                               DEPT_NAME = "Biology")


        testingLSF = LaborStatusForm.create(StudentName = "Tyler Parton",
                                            termCode = 200000,
                                            studentSupervisee = "B00000002",
                                            supervisor = Supervisor.get_by_id("B00000001"),
                                            department = testingDept.departmentID,
                                            jobType = "Primary",
                                            WLS = "1",
                                            POSN_TITLE = "Student Programmer",
                                            POSN_CODE = "S61407")

        testingFormHistory = (FormHistory.create(formID = testingLSF.laborStatusFormID,
                                               historyType = "Labor Status Form",
                                               releaseForm = None,
                                               adjustedForm = None,
                                               overloadForm = None,
                                               createdBy = testingSupervisor.ID,
                                               createdDate = "2020-04-14",
                                               reviewedDate = "2020-04-14",
                                               reviewedBy = None,
                                               status = "Approved"))


        with app.test_request_context(
            "/sle", method="POST", data={"submit_as_final": True}):
                createSLEform = sle(testingLSF.laborStatusFormID)
                assert StudentLaborEvaluation.get_or_none(StudentLaborEvaluation.formHistoryID == testingFormHistory.formHistoryID) != None
                transaction.rollback()
