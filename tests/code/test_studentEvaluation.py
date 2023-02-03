import pytest
from app.controllers.main_routes.studentLaborEvaluation import sle
from app import app
import pytest
from app.models import mainDB
from app.models.laborStatusForm import LaborStatusForm
from app.models.formHistory import FormHistory
from app.models.student import Student
from app.models.supervisor import Supervisor
from app.logic.userInsertFunctions import createLaborStatusForm

import json


@pytest.mark.integration
def testCreateStudentEval():
    with mainDB.atomic() as transaction:
        supervisorDept = Department.create(DEPT_NAME="Testing Department", ACCOUNT="6740", ORG="2114")
        testingTerm = Term.create(termCode = 200000, termName = "Testing Term")
        testingStudent =  (Student.create(
                ID="B00000002",
                FIRST_NAME="Tyler",
                LAST_NAME="Parton",
                STU_EMAIL="partont@whatever.edu",
                STU_CPO="Unknown"
                ))
        testingSupervisor = (Supervisor.create(ID = "B00000001",
                            PIDM = 75,
                            FIRST_NAME = "Not",
                            LAST_NAME = "Scott",
                            EMAIL = "None",
                            CPO = "None",
                            DEPT_NAME = "Testing Department"))
        testingFormHistory = (FormHistory.create(formID = inDeptForm.laborStatusFormID,
                                               historyType = "Labor Status Form",
                                               releaseForm = None,
                                               adjustedForm = None,
                                               overloadForm = None,
                                               createdBy = 1,
                                               createdDate = "2020-04-14",
                                               reviewedDate = None,
                                               reviewedBy = None,
                                               status = "Approved"))

        createLaborStatusForm("B00000002", "B00000001", supervisorDept.ID, testingTerm)
        with app.test_request_context(
            "/sle", method="POST", data=termCodeDict):
                createSLEform = sle()

                transaction.rollback()
