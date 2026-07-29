import pytest
from flask import g

from app import app
from app.controllers.main_routes.departmentPortal import (
    addUserToDept,
    removeMember,
    searchMember,
    updateCoordinator,
    updateEligibility,
)
from app.models import mainDB
from app.models.department import Department
from app.models.supervisor import Supervisor
from app.models.supervisorDepartment import SupervisorDepartment
from app.models.user import User


@pytest.mark.integration
def test_searchMember_returns_matching_supervisor():
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

        assert len(data) == 1
        assert data[0]["bnumber"] == "B99000001"
        assert data[0]["firstName"] == "Test"
        assert data[0]["lastName"] == "Supervisor"

        transaction.rollback()


@pytest.mark.integration
def test_manage_member_actions():
    with mainDB.atomic() as transaction:
        dept = Department.create(
            DEPT_NAME="Manage Members Test Department",
            ACCOUNT="69001",
            ORG="2991",
            departmentCompliance=True
        )

        adminSupervisor = Supervisor.create(
            ID="B99000002",
            PIDM=990002,
            legal_name="Admin",
            LAST_NAME="Supervisor",
            EMAIL="admin.supervisor@berea.edu",
            CPO="9902",
            DEPT_NAME="Labor Department"
        )

        memberSupervisor = Supervisor.create(
            ID="B99000003",
            PIDM=990003,
            legal_name="Member",
            LAST_NAME="Supervisor",
            EMAIL="member.supervisor@berea.edu",
            CPO="9903",
            DEPT_NAME="Manage Members Test Department",
            isBanned=False
        )

        admin = User.create(
            student=None,
            supervisor=adminSupervisor,
            username="testmanageadmin",
            isLaborAdmin=True,
            isFinancialAidAdmin=False,
            isSaasAdmin=False
        )

        SupervisorDepartment.create(
            supervisor=memberSupervisor,
            department=dept,
            isCoordinator=False
        )

        with app.test_request_context(
            "/members/update_coordinator",
            method="POST",
            data={
                "supervisorID": memberSupervisor.ID,
                "departmentID": dept.departmentID,
                "isCoordinator": "true"
            }
        ):
            g.currentUser = admin
            response = updateCoordinator()

        member = SupervisorDepartment.get(
            SupervisorDepartment.supervisor == memberSupervisor,
            SupervisorDepartment.department == dept
        )

        assert response[1] == 200
        assert member.isCoordinator

        with app.test_request_context(
            "/members/update_eligibility",
            method="POST",
            data={
                "supervisorID": memberSupervisor.ID
            }
        ):
            g.currentUser = admin
            response = updateEligibility()

        memberSupervisor = Supervisor.get(Supervisor.ID == "B99000003")

        assert response[1] == 200
        assert memberSupervisor.isBanned

        with app.test_request_context(
            "/members/add",
            method="POST",
            data={
                "supervisorID": memberSupervisor.ID,
                "departmentID": dept.departmentID
            }
        ):
            g.currentUser = admin
            response = addUserToDept()

        assert response == "False"

        with app.test_request_context(
            "/members/remove",
            method="DELETE",
            data={
                "supervisorID": memberSupervisor.ID,
                "departmentID": dept.departmentID
            }
        ):
            g.currentUser = admin
            response = removeMember()

        member = SupervisorDepartment.get_or_none(
            supervisor=memberSupervisor.ID,
            department=dept.departmentID
        )

        assert response[1] == 200
        assert member is None

        transaction.rollback()


@pytest.mark.integration
def test_addUserToDept_adds_existing_supervisor():
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
            response = addUserToDept()

        member = SupervisorDepartment.get_or_none(
            supervisor=newSupervisor.ID,
            department=dept.departmentID
        )

        assert response == "True"
        assert member is not None

        transaction.rollback()