import pytest
from flask import session
import re
from datetime import date
from flask import render_template, request, json, redirect, session, url_for, send_file, g, flash, jsonify
from peewee import JOIN, DoesNotExist, fn, Case
from functools import reduce
import operator
from app.logic.userInsertFunctions import createSupervisorFromTracy
from app.models.department import Department
from app.models.supervisor import Supervisor
from app.models.supervisorDepartment import SupervisorDepartment
from app.models.student import Student
from app.models.laborStatusForm import LaborStatusForm
from app.models.formHistory import FormHistory
from app.models.laborReleaseForm import LaborReleaseForm
from app.models.term import Term
from app.controllers.admin_routes.allPendingForms import checkAdjustment
from app.controllers.main_routes import main_bp
from app.logic.download import CSVMaker, saveFormSearchResult, retrieveFormSearchResult
from app.logic.search import getDepartmentsForSupervisor, searchPerson, searchSupervisorPortal
from app.login_manager import require_login, logout
from app.logic.getTableData import getDatatableData
from app.logic.banner import Banner
from flask import abort
from app.logic.search import limitSearchByUserDepartment, studentDbToDict, usernameFromEmail


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