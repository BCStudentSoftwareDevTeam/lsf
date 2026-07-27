from datetime import date
from types import SimpleNamespace

import pytest
from werkzeug.exceptions import NotFound

from app import app
import app.logic.manageMembers as manageMembersLogic
from app.logic.manageMembers import (
    attachPositionCounts,
    getCurrentDepartment,
    getDepartmentMembers,
    getStudentCounts,
    supervisorsDbToDict,
)
from app.models import mainDB
from app.models.department import Department
from app.models.formHistory import FormHistory
from app.models.laborReleaseForm import LaborReleaseForm
from app.models.laborStatusForm import LaborStatusForm
from app.models.student import Student
from app.models.supervisor import Supervisor
from app.models.supervisorDepartment import SupervisorDepartment
from app.models.term import Term


@pytest.mark.integration
def test_getCurrentDepartment():
    with mainDB.atomic() as transaction:
        testDept = Department.create(
            ORG=2114,
            ACCOUNT="60000",
            DEPT_NAME="Computer Science"
        )

        with app.test_request_context():
            # Case 1: verify the department is found
            dept = getCurrentDepartment(org=2114, account="60000")

            assert dept.departmentID == testDept.departmentID
            assert dept.DEPT_NAME == "Computer Science"

        with app.test_request_context():
            # Case 2: confirm a non-existent org/account combo 404s
            with pytest.raises(NotFound):
                getCurrentDepartment(org=9999, account="00000")

        transaction.rollback()


@pytest.mark.integration
def test_getDepartmentMembers():
    with mainDB.atomic() as transaction:
        testDept = Department.create(
            ORG=2114,
            ACCOUNT="60000",
            DEPT_NAME="Computer Science"
        )

        testingSupervisor = Supervisor.create(
            ID="B00000001",
            PIDM=75,
            legal_name="Not",
            LAST_NAME="Scott",
            EMAIL="None",
            CPO="None",
            DEPT_NAME="Computer Science"
        )

        SupervisorDepartment.create(
            supervisor=testingSupervisor.ID,
            department=testDept.departmentID
        )

        with app.test_request_context():
            # Case 1: confirm the supervisor tied to the department comes back
            members = getDepartmentMembers(testDept)

            assert len(members) == 1
            assert members[0].supervisor.ID == testingSupervisor.ID
            assert members[0].supervisor.LAST_NAME == "Scott"
            assert members[0].department_id == testDept.departmentID

        transaction.rollback()


def test_supervisorsDbToDict_formats_supervisor_data():
    supervisor = SimpleNamespace(
        EMAIL=" scott.heggen@berea.edu ",
        FIRST_NAME=" Scott ",
        LAST_NAME=" Heggen ",
        ID=" B12345678 ",
        DEPT_NAME=" Computer Science "
    )

    result = supervisorsDbToDict(supervisor)

    assert result == {
        "username": "scott.heggen",
        "firstName": "Scott",
        "lastName": "Heggen",
        "bnumber": "B12345678",
        "department": "Computer Science",
        "type": "Supervisor"
    }


def test_currentAcademicYear_before_july(monkeypatch):
    class FakeDate:
        @staticmethod
        def today():
            return date(2026, 6, 15)

    monkeypatch.setattr(manageMembersLogic, "date", FakeDate)

    assert manageMembersLogic.currentAcademicYear() == (2025, 2026)


def test_currentAcademicYear_after_july(monkeypatch):
    class FakeDate:
        @staticmethod
        def today():
            return date(2026, 7, 1)

    monkeypatch.setattr(manageMembersLogic, "date", FakeDate)

    assert manageMembersLogic.currentAcademicYear() == (2026, 2027)


def test_attachPositionCounts_adds_existing_counts():
    members = [
        SimpleNamespace(
            department_id=1,
            supervisor_id="B00000001"
        )
    ]

    counts = {
        (1, "B00000001"): {
            "active_primary_positions": 2,
            "pending_primary_positions": 1,
            "active_secondary_positions": 3,
            "pending_secondary_positions": 4
        }
    }

    result = attachPositionCounts(members, counts)

    assert result[0].active_primary_positions == 2
    assert result[0].pending_primary_positions == 1
    assert result[0].active_secondary_positions == 3
    assert result[0].pending_secondary_positions == 4


def test_attachPositionCounts_defaults_missing_counts_to_zero():
    members = [
        SimpleNamespace(
            department_id=1,
            supervisor_id="B00000001"
        )
    ]

    result = attachPositionCounts(members, {})

    assert result[0].active_primary_positions == 0
    assert result[0].pending_primary_positions == 0
    assert result[0].active_secondary_positions == 0
    assert result[0].pending_secondary_positions == 0


@pytest.mark.integration
def test_getStudentCounts_counts_active_and_pending_positions():
    with mainDB.atomic() as transaction:
        testFormIds = [9001, 9002, 9003, 9004]

        LaborStatusForm.delete().where(
            LaborStatusForm.laborStatusFormID.in_(testFormIds)
        ).execute()

        dept = Department.create(
            ORG=2114,
            ACCOUNT="60000",
            DEPT_NAME="Computer Science"
        )

        supervisor = Supervisor.create(
            ID="B00000001",
            PIDM=75,
            legal_name="Scott Heggen",
            LAST_NAME="Heggen",
            EMAIL="heggen@berea.edu",
            CPO="None",
            DEPT_NAME="Computer Science"
        )

        student, created = Student.get_or_create(
            ID="B90000001",
            defaults={
                "PIDM": 900001
            }
        )

        term, created = Term.get_or_create(
            termCode=202500,
            defaults={
                "termName": "AY 2025-2026",
                "termStart": "2025-08-01",
                "termEnd": "2026-05-01",
                "termState": 1,
                "primaryCutOff": "2025-09-01",
                "adjustmentCutOff": "2025-10-01"
            }
        )

        LaborStatusForm.create(
            laborStatusFormID=9001,
            termCode=term,
            studentName="Student One",
            studentSupervisee=student,
            supervisor=supervisor,
            department=dept,
            jobType="Primary",
            weeklyHours=10,
            studentConfirmation=True
        )

        LaborStatusForm.create(
            laborStatusFormID=9002,
            termCode=term,
            studentName="Student Two",
            studentSupervisee=student,
            supervisor=supervisor,
            department=dept,
            jobType="Primary",
            weeklyHours=10,
            studentConfirmation=None
        )

        LaborStatusForm.create(
            laborStatusFormID=9003,
            termCode=term,
            studentName="Student Three",
            studentSupervisee=student,
            supervisor=supervisor,
            department=dept,
            jobType="Secondary",
            weeklyHours=5,
            studentConfirmation=True
        )

        LaborStatusForm.create(
            laborStatusFormID=9004,
            termCode=term,
            studentName="Student Four",
            studentSupervisee=student,
            supervisor=supervisor,
            department=dept,
            jobType="Secondary",
            weeklyHours=5,
            studentConfirmation=None
        )

        counts = getStudentCounts(dept)
        row = counts[(dept.departmentID, supervisor.ID)]

        assert row["active_primary_positions"] == 1
        assert row["pending_primary_positions"] == 1
        assert row["active_secondary_positions"] == 1
        assert row["pending_secondary_positions"] == 1

        transaction.rollback()


@pytest.mark.integration
def test_getStudentCounts_excludes_released_forms():
    with mainDB.atomic() as transaction:
        testFormIds = [9011, 9012]
        testReleaseFormId = 9011

        # Clean up old test data if the test was run before.
        FormHistory.delete().where(
            FormHistory.formID.in_(testFormIds)
        ).execute()

        LaborReleaseForm.delete().where(
            LaborReleaseForm.laborReleaseFormID == testReleaseFormId
        ).execute()

        LaborStatusForm.delete().where(
            LaborStatusForm.laborStatusFormID.in_(testFormIds)
        ).execute()

        dept = Department.create(
            ORG=2115,
            ACCOUNT="60001",
            DEPT_NAME="Computer Science Test"
        )

        supervisor = Supervisor.create(
            ID="B00000002",
            PIDM=76,
            legal_name="Test Supervisor",
            LAST_NAME="Supervisor",
            EMAIL="testsupervisor@berea.edu",
            CPO="None",
            DEPT_NAME="Computer Science Test"
        )

        student, created = Student.get_or_create(
            ID="B90000002",
            defaults={
                "PIDM": 900002
            }
        )

        term, created = Term.get_or_create(
            termCode=202500,
            defaults={
                "termName": "AY 2025-2026",
                "termStart": "2025-08-01",
                "termEnd": "2026-05-01",
                "termState": 1,
                "primaryCutOff": "2025-09-01",
                "adjustmentCutOff": "2025-10-01"
            }
        )

        # This form should be counted.
        LaborStatusForm.create(
            laborStatusFormID=9011,
            termCode=term,
            studentName="Active Student",
            studentSupervisee=student,
            supervisor=supervisor,
            department=dept,
            jobType="Primary",
            weeklyHours=10,
            studentConfirmation=True
        )

        # This form would normally be counted, but it has an approved release form.
        LaborStatusForm.create(
            laborStatusFormID=9012,
            termCode=term,
            studentName="Released Student",
            studentSupervisee=student,
            supervisor=supervisor,
            department=dept,
            jobType="Primary",
            weeklyHours=10,
            studentConfirmation=True
        )

        releaseForm = LaborReleaseForm.create(
            laborReleaseFormID=testReleaseFormId,
            conditionAtRelease="satisfactory",
            releaseDate=date.today(),
            reasonForRelease="Test release"
        )

        FormHistory.create(
            formHistoryID=9012,
            formID=9012,
            historyType="Labor Release Form",
            releaseForm=releaseForm,
            createdBy=1,
            createdDate=date.today(),
            status="Approved"
        )

        counts = getStudentCounts(dept)
        row = counts[(dept.departmentID, supervisor.ID)]

        assert row["active_primary_positions"] == 1
        assert row["pending_primary_positions"] == 0
        assert row["active_secondary_positions"] == 0
        assert row["pending_secondary_positions"] == 0

        transaction.rollback()