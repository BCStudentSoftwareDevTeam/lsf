from datetime import date

import pytest
from werkzeug.exceptions import NotFound

from app import app
from app.logic.manageMembers import (
    attachPositionCounts,
    getCurrentDeptMembers,
    getStudentCounts,
)
from app.logic.getSupervisors import buildSupervisorDisplay

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
def test_buildSupervisorDisplay_returns_portal_and_search_fields():
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
def test_getCurrentDeptMembers():
    with mainDB.atomic() as transaction:
        dept = Department.create(
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

        SupervisorDepartment.create(
            supervisor=supervisor,
            department=dept
        )

        with app.test_request_context():
            currentDept, members = getCurrentDeptMembers("2995", "69101")

        assert currentDept.departmentID == dept.departmentID
        assert len(members) == 1
        assert members[0].supervisor.ID == supervisor.ID
        assert members[0].department.departmentID == dept.departmentID

        with app.test_request_context():
            with pytest.raises(NotFound):
                getCurrentDeptMembers("0000", "0000")

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

        member = SupervisorDepartment.create(
            supervisor=supervisor,
            department=dept
        )

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
@pytest.mark.integration
def test_getStudentCounts_counts_active_pending_positions_and_ignores_released_form():
    with mainDB.atomic() as transaction:
        testFormIds = [991001, 991002, 991003, 991004, 991005]

        FormHistory.delete().where(FormHistory.formID.in_(testFormIds)).execute()
        LaborStatusForm.delete().where(
            LaborStatusForm.laborStatusFormID.in_(testFormIds)
        ).execute()

        # Given one department with one supervisor and one student
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

        term = Term.get_or_create(
            termCode=209900,
            defaults={
                "termName": "AY 2099-2100",
                "termStart": "2099-08-01",
                "termEnd": "2100-05-01",
                "termState": 1,
                "primaryCutOff": "2099-09-01",
                "adjustmentCutOff": "2099-10-01"
            }
        )[0]

        # And the student has active and pending primary/secondary positions
        testForms = [
            (991001, "Active Primary", "Primary", True),
            (991002, "Pending Primary", "Primary", None),
            (991003, "Active Secondary", "Secondary", True),
            (991004, "Pending Secondary", "Secondary", None),
            (991005, "Released Primary", "Primary", True),
        ]

        for formID, studentName, jobType, studentConfirmation in testForms:
            LaborStatusForm.create(
                laborStatusFormID=formID,
                termCode=term,
                studentName=studentName,
                studentSupervisee=student,
                supervisor=supervisor,
                department=dept,
                jobType=jobType,
                weeklyHours=10,
                studentConfirmation=studentConfirmation
            )

        # And one approved primary position has been released
        releaseForm = LaborReleaseForm.create(
            laborReleaseFormID=991005,
            conditionAtRelease="satisfactory",
            releaseDate=date.today(),
            reasonForRelease="Test release"
        )

        FormHistory.create(
            formHistoryID=991005,
            formID=991005,
            historyType="Labor Release Form",
            releaseForm=releaseForm,
            createdBy=1,
            createdDate=date.today(),
            status="Approved"
        )

        # When getStudentCounts runs
        counts = getStudentCounts(dept)
        row = counts[(dept.departmentID, supervisor.ID)]

        # Then it counts each active/pending position type and ignores the released form
        assert row["active_primary_positions"] == 1
        assert row["pending_primary_positions"] == 1
        assert row["active_secondary_positions"] == 1
        assert row["pending_secondary_positions"] == 1

        transaction.rollback()