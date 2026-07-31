import pytest
from flask import g

from app import app
from app.controllers.main_routes.departmentPortal import addUserToDept, searchMember
from app.models import mainDB
from app.models.department import Department
from app.models.supervisor import Supervisor
from app.models.supervisorDepartment import SupervisorDepartment
from app.models.user import User


@pytest.mark.integration
def test_searchMember_returns_matching_supervisor():
    """Search member returns the supervisor matching the given B-number."""
    with mainDB.atomic() as transaction:
        supervisor = Supervisor.create(
            ID="B99000001",
            PIDM=990001,
            legal_name="Test",
            LAST_NAME="Supervisor",
            EMAIL="test.supervisor@berea.edu",
            CPO="9901",
            DEPT_NAME="Computer Science"
        )

        admin = User.create(
            student=None,
            supervisor=supervisor,
            username="testadminsearch",
            isLaborAdmin=True,
            isFinancialAidAdmin=False,
            isSaasAdmin=False
        )

        with app.test_request_context("/members/search/B99000001"):
            g.currentUser = admin
            response = searchMember("B99000001")
            data = response.get_json()

        assert data[0]["bnumber"] == "B99000001"
        assert data[0]["firstName"] == "Test"
        assert data[0]["lastName"] == "Supervisor"

        transaction.rollback()


@pytest.mark.integration
def test_addUserToDept_adds_existing_supervisor():
    """Add user to department creates a supervisor-department record."""
    with mainDB.atomic() as transaction:
        dept = Department.create(
            DEPT_NAME="Add Member Test Department",
            ACCOUNT="69002",
            ORG="2992",
            departmentCompliance=True
        )

        adminSupervisor = Supervisor.create(
            ID="B99000004",
            PIDM=990004,
            legal_name="Admin",
            LAST_NAME="User",
            EMAIL="admin.user@berea.edu",
            CPO="9904",
            DEPT_NAME="Labor Department"
        )

        newSupervisor = Supervisor.create(
            ID="B99000005",
            PIDM=990005,
            legal_name="New",
            LAST_NAME="Member",
            EMAIL="new.member@berea.edu",
            CPO="9905",
            DEPT_NAME="Add Member Test Department"
        )

        admin = User.create(
            student=None,
            supervisor=adminSupervisor,
            username="testaddadmin",
            isLaborAdmin=True,
            isFinancialAidAdmin=False,
            isSaasAdmin=False
        )

        with app.test_request_context(
            "/members/add",
            method="POST",
            data={
                "supervisorID": newSupervisor.ID,
                "departmentID": dept.departmentID
            }
        ):
            g.currentUser = admin
            response, statusCode = addUserToDept()
            data = response.get_json()

        member = SupervisorDepartment.get_or_none(
            supervisor=newSupervisor.ID,
            department=dept.departmentID
        )

        assert statusCode == 200
        assert data["success"] is True
        assert data["message"] == "Supervisor added to department."
        assert member is not None

        transaction.rollback()