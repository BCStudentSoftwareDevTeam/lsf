import pytest
import json

from werkzeug.exceptions import BadRequest
from unittest.mock import patch

from flask import g 
from flask_wtf.csrf import CSRFProtect

from app import app

from app.models import mainDB
from app.models.laborStatusForm import LaborStatusForm
from app.models.department import Department
from app.models.term import Term
from app.models.formHistory import FormHistory
from app.models.allocation import Allocation

from app.controllers.admin_routes import manage_departments

from app.logic.manageDepartments import *


# The following test file is for testing the manageDepartments logic file and its associated functions and queries. 
# It is designed to ensure that the manageDepartments functionality works as expected and returns the correct data.


@pytest.mark.integration
def test_generateAdjacentYears():
    with app.app_context():
        with mainDB.atomic() as transaction:

            # THE FIRST TEST
            g.openTerm, _ = Term.get_or_create(
                termCode = 202500,
                defaults={"termName": "AY 2025-2026", "isAcademicYear": True}
            )
            
            currentYear, previousYear, followingYear = generateAdjacentYears(202500)
            
            assert currentYear.termCode == 202500
            assert currentYear.termName == "AY 2025-2026"

            assert previousYear.termCode == 202400
            assert previousYear.termName == "AY 2024-2025"

            assert followingYear.termCode == 202600
            assert followingYear.termName == "AY 2026-2027"

            transaction.rollback()


            # THE SECOND TEST
            with pytest.raises(BadRequest):
                generateAdjacentYears(202300)
                transaction.rollback()

            with pytest.raises(BadRequest):
                generateAdjacentYears(202200)
                transaction.rollback()

            with pytest.raises(BadRequest):
                generateAdjacentYears(2025)
                transaction.rollback()
            
            with pytest.raises(BadRequest):
                generateAdjacentYears(True)
                transaction.rollback()

            with pytest.raises(BadRequest):
                generateAdjacentYears(False)
                transaction.rollback()

            with pytest.raises(BadRequest):
                generateAdjacentYears("SELECT lsf DELETE *")
                transaction.rollback()


            #THE THIRD TEST 
            g.openTerm, _ = Term.get_or_create(
                termCode = 198200,
                defaults={"termName": "AY 1982-1983", "isAcademicYear": True}
            )

            currentYear, previousYear, followingYear = generateAdjacentYears(198200)
            
            assert currentYear.termCode == 198200
            assert currentYear.termName == "AY 1982-1983"

            assert previousYear.termCode == 198100
            assert previousYear.termName == "AY 1981-1982"

            assert followingYear.termCode == 198300
            assert followingYear.termName == "AY 1983-1984"

            assert isinstance(currentYear.termCode, int)
            assert isinstance(previousYear.termCode, int)
            assert isinstance(followingYear.termCode, int)

            assert currentYear.termName.split(" ")[0] == "AY"
            assert previousYear.termName.split(" ")[0] == "AY"
            assert followingYear.termName.split(" ")[0] == "AY"

            assert currentYear.termName.split(" ")[1] == "1982-1983"
            assert previousYear.termName.split(" ")[1] == "1981-1982"
            assert followingYear.termName.split(" ")[1] == "1983-1984"

            transaction.rollback()





# @pytest.mark.integration
# def test_ManageDepartmentsPrimaryandSecondary():
#     with mainDB.atomic() as transaction:
        
#         assert True

#         testingDept = Department.get_or_create(DEPT_NAME="Computer Science", ACCOUNT="6740", ORG="2114")
#         testingTerm = Term.get_or_create(
#             termCode=f"{2028}00",
#             termName=f"AY {2028}-{2029}",
#             termStart=f"{2028}-08-01",
#             termEnd=f"{2029}-05-01",
#             termState=0,
#             primaryCutOff=f"{2028}-09-01",
#             adjustmentCutOff=f"{2029}-10-01"
#         )
#         # Might need an additional allocation wherer isFinal is True for testing purposes.
#         testingAllocation = Allocation.get_or_create(
#             termCode=testingTerm.termCode,
#             department=testingDept.departmentID,
#             isFinal=False,
#             approvedOn=None,
#             approvedBy=None,
#             justification="Downscaling due to decrease in student enrollment caused by current economic conditions",
#             primary_10= 2,
#             primary_12= 2,
#             primary_15= 1,
#             primary_20= 0,
#             secondary_5= 1,
#             secondary_10= 0,
#             breakHours= 260,
#         )
#         # Might need to create different test data for different lsf statuses.
#         testingLSF = LaborStatusForm.get_or_create(
#             laborStatusFormID=2,
#             termCode_id=testingTerm.termCode,
#             studentName="Alex Bryant",
#             studentSupervisee_id="B00841417",
#             supervisor_id="B12361006",
#             department_id=testingDept.departmentID,
#             jobType="Primary",
#             WLS=1,
#             POSN_TITLE="Student Programmer",
#             POSN_CODE="S61407",
#             weeklyHours=10,
#             startDate=f"2028-04-01",
#             endDate=f"2029-09-01",
#             studentConfirmation=True
#         )
#         # Might need to create different test data for different form statuses.
#         testingFormHistory = FormHistory.get_or_create(
#             formHistoryID=2,
#             formID_id="2",
#             historyType_id="Labor Status Form",
#             createdBy_id=1,
#             createdDate=f"2025-04-14",
#             status="Active"
#         )

#         assert True

#         # transaction.rollback()

#     testCreation = {"",
#                         "",}

#     testReset = {"resetConfirmation": True}

#     with app.test_request_context( "/manage_departments", method="POST", data=testCreation):
#                 app.config['WTF_CSRF_ENABLED'] = False
#                 app.config['show_queries'] = False
                

#     with app.test_request_context( "/manage_departments", method="POST", data=testReset):
#                 app.config['WTF_CSRF_ENABLED'] = False
#                 app.config['show_queries'] = False