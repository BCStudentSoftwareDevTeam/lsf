import pytest
from flask import g

from app import app
from app.controllers.main_routes.departmentPortal import addUserToDept
from app.models import mainDB
from app.models.department import Department
from app.models.supervisor import Supervisor
from app.models.supervisorDepartment import SupervisorDepartment
from app.models.user import User


@pytest.mark.integration
def test_addUserToDept():
    """Add user to department handles add, duplicate, and missing data cases."""
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

        assert statusCode == 200
        assert data["success"] is False
        assert data["message"] == "Supervisor already exists in this department."

        with app.test_request_context(
            "/members/add",
            method="POST",
            data={}
        ):
            g.currentUser = admin
            response, statusCode = addUserToDept()
            data = response.get_json()

        assert statusCode == 400
        assert data["success"] is False
        assert data["message"] == "Missing supervisor or department."

        transaction.rollback()