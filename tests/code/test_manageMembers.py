from datetime import date

import pytest

from app.logic.getSupervisors import buildSupervisorDisplay, getSupervisorDepartments
from app.logic.manageMembers import (
    attachPositionCounts,
    getActivePendingPositionCounts,
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
def test_getSupervisorDepartments():
    with mainDB.atomic() as transaction:
        department = Department.create(
            DEPT_NAME="Current Members Department",
            ACCOUNT="69101",
            ORG="2995",
            departmentCompliance=True
        )

        supervisor = Supervisor.create(
            ID="B99100002",
            PIDM=991002,
            legal_name="Current",
            LAST_NAME="Member",
            EMAIL="current.member@berea.edu",
            CPO="9912",
            DEPT_NAME="Current Members Department"
        )

        SupervisorDepartment.create(supervisor=supervisor, department=department)

        members = getSupervisorDepartments(department)

        assert len(members) == 1
        assert members[0].supervisor.ID == supervisor.ID
        assert members[0].department.departmentID == department.departmentID

        transaction.rollback()


@pytest.mark.integration
def test_buildSupervisorDisplay():
    with mainDB.atomic() as transaction:
        supervisor = Supervisor.create(
            ID="B99100001",
            PIDM=991001,
            legal_name=" Test ",
            LAST_NAME=" Supervisor ",
            EMAIL=" test.supervisor@berea.edu ",
            CPO="9911",
            DEPT_NAME=" Computer Science "
        )

        result = buildSupervisorDisplay(supervisor)

        assert result["username"] == "test.supervisor"
        assert result["firstName"] == "Test"
        assert result["lastName"] == "Supervisor"
        assert result["bnumber"] == "B99100001"
        assert result["department"] == "Computer Science"
        assert result["type"] == "Supervisor"
        assert result["name"] == "Test Supervisor"
        assert result["email"] == "test.supervisor@berea.edu"

        transaction.rollback()


@pytest.mark.integration
def test_attachPositionCounts():
    with mainDB.atomic() as transaction:
        dept = Department.create(
            DEPT_NAME="Position Count Department",
            ACCOUNT="69102",
            ORG="2996",
            departmentCompliance=True
        )

        supervisor = Supervisor.create(
            ID="B99100003",
            PIDM=991003,
            legal_name="Count",
            LAST_NAME="Member",
            EMAIL="count.member@berea.edu",
            CPO="9913",
            DEPT_NAME="Position Count Department"
        )

        member = SupervisorDepartment.create(supervisor=supervisor, department=dept)

        counts = {
            (dept.departmentID, supervisor.ID): {
                "active_primary_positions": 2,
                "pending_primary_positions": 1,
                "active_secondary_positions": 3,
                "pending_secondary_positions": 4
            }
        }

        members = attachPositionCounts([member], counts)

        assert members[0].active_primary_positions == 2
        assert members[0].pending_primary_positions == 1
        assert members[0].active_secondary_positions == 3
        assert members[0].pending_secondary_positions == 4

        members = attachPositionCounts([member], {})

        assert members[0].active_primary_positions == 0
        assert members[0].pending_primary_positions == 0
        assert members[0].active_secondary_positions == 0
        assert members[0].pending_secondary_positions == 0

        transaction.rollback()


@pytest.mark.integration
def test_getActivePendingPositionCounts():
    with mainDB.atomic() as transaction:
        testFormIds = [991001, 991002, 991003, 991004, 991005, 991006, 991007]

        FormHistory.delete().where(FormHistory.formID.in_(testFormIds)).execute()
        LaborStatusForm.delete().where(
            LaborStatusForm.laborStatusFormID.in_(testFormIds)
        ).execute()
        LaborReleaseForm.delete().where(
            LaborReleaseForm.laborReleaseFormID == 991005
        ).execute()

        dept = Department.create(
            DEPT_NAME="Student Count Department",
            ACCOUNT="69104",
            ORG="2998",
            departmentCompliance=True
        )

        supervisor = Supervisor.create(
            ID="B99100005",
            PIDM=991005,
            legal_name="Student",
            LAST_NAME="Counter",
            EMAIL="student.counter@berea.edu",
            CPO="9915",
            DEPT_NAME="Student Count Department"
        )

        student = Student.create(
            ID="B99110001",
            PIDM=991101,
            legal_name="Test",
            LAST_NAME="Student",
            CLASS_LEVEL="Senior",
            STU_EMAIL="test.student@berea.edu"
        )

        currentTerm = Term.get_or_create(
            termCode=202600,
            defaults={
                "termName": "AY 2026-2027",
                "termStart": "2026-08-01",
                "termEnd": "2027-05-01",
                "termState": 1,
                "primaryCutOff": "2026-09-01",
                "adjustmentCutOff": "2026-10-01"
            }
        )[0]

        oldTerm = Term.get_or_create(
            termCode=202500,
            defaults={
                "termName": "AY 2025-2026",
                "termStart": "2025-08-01",
                "termEnd": "2026-05-01",
                "termState": 1,
                "primaryCutOff": "2025-09-01",
                "adjustmentCutOff": "2025-10-01"
            }
        )[0]

        testForms = [
            (991001, currentTerm, "Active Primary", "Primary", "Approved"),
            (991002, currentTerm, "Pending Primary", "Primary", "Pending"),
            (991003, currentTerm, "Active Secondary", "Secondary", "Approved"),
            (991004, currentTerm, "Pending Secondary", "Secondary", "Pre-Student Approval"),
            (991005, currentTerm, "Released Primary", "Primary", "Approved"),
            (991006, currentTerm, "Denied Primary", "Primary", "Denied by Admin"),
            (991007, oldTerm, "Old Year Primary", "Primary", "Approved"),
        ]

        for formID, term, studentName, jobType, formStatus in testForms:
            LaborStatusForm.create(
                laborStatusFormID=formID,
                termCode=term,
                studentName=studentName,
                studentSupervisee=student,
                supervisor=supervisor,
                department=dept,
                jobType=jobType,
                weeklyHours=10,
                studentConfirmation=True
            )

            FormHistory.create(
                formHistoryID=formID,
                formID=formID,
                historyType="Labor Status Form",
                createdBy=1,
                createdDate=date.today(),
                status=formStatus
            )

        releaseForm = LaborReleaseForm.create(
            laborReleaseFormID=991005,
            conditionAtRelease="satisfactory",
            releaseDate=date.today(),
            reasonForRelease="Test release"
        )

        FormHistory.create(
            formHistoryID=991105,
            formID=991005,
            historyType="Labor Release Form",
            releaseForm=releaseForm,
            createdBy=1,
            createdDate=date.today(),
            status="Approved"
        )

        counts = getActivePendingPositionCounts(dept)
        row = counts[(dept.departmentID, supervisor.ID)]

        assert row["active_primary_positions"] == 1
        assert row["pending_primary_positions"] == 1
        assert row["active_secondary_positions"] == 1
        assert row["pending_secondary_positions"] == 1

        transaction.rollback()