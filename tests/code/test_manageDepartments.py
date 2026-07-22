import pytest
from app import app
from flask_wtf.csrf import CSRFProtect
import json
from app.models import mainDB
from app.models.laborStatusForm import LaborStatusForm
from app.models.department import Department
from app.models.term import Term
from app.models.formHistory import FormHistory
from app.models.allocation import Allocation
from app.logic.manageDepartments import *
from werkzeug.exceptions import BadRequest
from unittest.mock import patch
from app.controllers.admin_routes.manage_departments import manage_departments
from flask import g, render_template


# The following test file is for testing the manageDepartments logic file and its associated functions and queries. 
# It is designed to ensure that the manageDepartments functionality works as expected and returns the correct data.


@pytest.mark.integration
def test_ManageDepartmentsPrimaryandSecondary():
    with mainDB.atomic() as transaction:
        
        assert True

        testingDept = Department.get_or_create(DEPT_NAME="Computer Science", ACCOUNT="6740", ORG="2114")
        testingTerm = Term.get_or_create(
            termCode=f"{2028}00",
            termName=f"AY {2028}-{2029}",
            termStart=f"{2028}-08-01",
            termEnd=f"{2029}-05-01",
            termState=0,
            primaryCutOff=f"{2028}-09-01",
            adjustmentCutOff=f"{2029}-10-01"
        )
        # Might need an additional allocation wherer isFinal is True for testing purposes.
        testingAllocation = Allocation.get_or_create(
            termCode=testingTerm.termCode,
            department=testingDept.departmentID,
            isFinal=False,
            approvedOn=None,
            approvedBy=None,
            justification="Downscaling due to decrease in student enrollment caused by current economic conditions",
            primary_10= 2,
            primary_12= 2,
            primary_15= 1,
            primary_20= 0,
            secondary_5= 1,
            secondary_10= 0,
            breakHours= 260,
        )
        # Might need to create different test data for different lsf statuses.
        testingLSF = LaborStatusForm.get_or_create(
            laborStatusFormID=2,
            termCode_id=testingTerm.termCode,
            studentName="Alex Bryant",
            studentSupervisee_id="B00841417",
            supervisor_id="B12361006",
            department_id=testingDept.departmentID,
            jobType="Primary",
            WLS=1,
            POSN_TITLE="Student Programmer",
            POSN_CODE="S61407",
            weeklyHours=10,
            startDate=f"2028-04-01",
            endDate=f"2029-09-01",
            studentConfirmation=True
        )
        # Might need to create different test data for different form statuses.
        testingFormHistory = FormHistory.get_or_create(
            formHistoryID=2,
            formID_id="2",
            historyType_id="Labor Status Form",
            createdBy_id=1,
            createdDate=f"2025-04-14",
            status="Active"
        )

        assert True

        # transaction.rollback()

    testCreation = {"",
                        "",}

    testReset = {"resetConfirmation": True}

    with app.test_request_context( "/manage_departments", method="POST", data=testCreation):
                app.config['WTF_CSRF_ENABLED'] = False
                app.config['show_queries'] = False
                

    with app.test_request_context( "/manage_departments", method="POST", data=testReset):
                app.config['WTF_CSRF_ENABLED'] = False
                app.config['show_queries'] = False

























@pytest.mark.integration
def test_checkAdmistratorRights():
    with app.test_request_context(), mainDB.atomic() as transaction: 
        user, _ = User.get_or_create(username = "pearcej", defaults={"isLaborAdmin": False})
        with patch("app.login_manager.require_login", return_value=user):
            response, status  = checkAdmistratorRights()
            assert status == 4032
        transaction.rollback()
    
    with app.test_request_context(), mainDB.atomic() as transaction: 
        user, _  = User.get_or_create(username = "samantha", defaults={"isLaborAdmin": True})
        with patch("app.login_manager.require_login", return_value=user):
            response, status  = checkAdmistratorRights()
            assert status == 500
        transaction.rollback()

    with app.test_request_context(), mainDB.atomic() as transaction: 
        user = None
        with patch("app.login_manager.require_login", return_value=user):
            response, status  = checkAdmistratorRights()
            assert status == 403
        transaction.rollback()
    
    
    

@pytest.mark.integration
def test_getUsedBreakHours():
    with mainDB.atomic() as transaction:
        ...

@pytest.mark.integration
def test_getActiveDepartmentsWithAllocation():
    ...

@pytest.mark.integration
def test_getAllocationStatus():
    ...

@pytest.mark.integration
def test_getLSFCountPrimaries():
    ...

@pytest.mark.integration
def test_getLSFCountSecondaries():
    ...

@pytest.mark.integration
def test_generateTermsForAdjacentYears():
    with app.app_context():
        g.openTerm.termCode = 2026
        assert generateTermsForAdjacentYears(g.openTerm.termCode) == (generateTerms(g.openTerm.termCode - 100), generateTerms(g.openTerm.termCode), generateTerms(g.openTerm.termCode + 100))
        assert generateTermsForAdjacentYears(g.openTerm.termCode-100) == (generateTerms(g.openTerm.termCode - 100), generateTerms(g.openTerm.termCode), generateTerms(g.openTerm.termCode + 100))
        assert generateTermsForAdjacentYears(g.openTerm.termCode+100) == (generateTerms(g.openTerm.termCode - 100), generateTerms(g.openTerm.termCode), generateTerms(g.openTerm.termCode + 100))

        with pytest.raises(BadRequest): 
            generateTermsForAdjacentYears(197200)
        
        with pytest.raises(BadRequest): 
            generateTermsForAdjacentYears(True)
        
        with pytest.raises(BadRequest): 
            generateTermsForAdjacentYears("197200")

        with pytest.raises(BadRequest): 
            generateTermsForAdjacentYears(1.2)