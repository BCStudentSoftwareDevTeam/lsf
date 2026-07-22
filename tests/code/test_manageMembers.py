import pytest
from flask import session
from werkzeug.exceptions import NotFound

from app import app
from app.models import mainDB
from app.models.department import Department
from app.models.supervisor import Supervisor
from app.models.supervisorDepartment import SupervisorDepartment
from app.logic.manageMembers import (
    getCurrentDepartment,
    getDepartmentMembers,
)

@pytest.mark.integration
def test_getCurrentDepartment():
    with mainDB.atomic() as transaction:
        testDept = Department.create(ORG = 2114,
                                     ACCOUNT = "60000",
                                     DEPT_NAME = "Computer Science")

        with app.test_request_context():
            # Case 1: verify the department is found and stashed in session
            dept = getCurrentDepartment(org = 2114, account = "60000")

            assert dept.departmentID == testDept.departmentID
            assert dept.DEPT_NAME == "Computer Science"
            assert session['current_department_id'] == testDept.departmentID
            assert session['current_department'] == "Computer Science"

        with app.test_request_context():
            # Case 2: confirm a non-existent org/account combo 404s
            with pytest.raises(NotFound):
                getCurrentDepartment(org = 9999, account = "00000")

        transaction.rollback()


@pytest.mark.integration
def test_getDepartmentMembers():
    with mainDB.atomic() as transaction:
        testDept = Department.create(ORG = 2114,
                                     ACCOUNT = "60000",
                                     DEPT_NAME = "Computer Science")

        testingSupervisor = Supervisor.create(ID = "B00000001",
                                              PIDM = 75,
                                              legal_name = "Not",
                                              LAST_NAME = "Scott",
                                              EMAIL = "None",
                                              CPO = "None",
                                              DEPT_NAME = "Computer Science")

        SupervisorDepartment.create(supervisor = testingSupervisor.ID,
                                    department = testDept.departmentID)

        with app.test_request_context():
            # Case 1: confirm the supervisor tied to the department comes back
            members = getDepartmentMembers(testDept)

            assert len(members) == 1
            assert members[0]['supervisor'] == testingSupervisor.ID
            assert members[0]['LAST_NAME'] == "Scott"

        transaction.rollback()