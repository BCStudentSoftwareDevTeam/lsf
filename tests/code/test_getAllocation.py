from datetime import date

import pytest
from app.models import mainDB
from app.models.department import Department
from app.models.term import Term
from app.models.allocation import Allocation
from app.models.laborStatusForm import LaborStatusForm
from app.models.student import Student
from app.models.supervisor import Supervisor
from app.models.formHistory import FormHistory
from app.models.historyType import HistoryType
from app.models.status import Status
from app.models.user import User
from app.logic.getAllocation import getDepartmentAllocationSummary, countWorkers, getBreakHours


def _createFormHistory(form, statusName):
    """Attach a FormHistory row to a LaborStatusForm, since getBreakHours now
    only counts forms with an approved "Labor Status Form" history entry."""
    user = User.create(username=f"testuser_{form.laborStatusFormID}")
    historyType = HistoryType.get(HistoryType.historyTypeName == "Labor Status Form")
    status = Status.get(Status.statusName == statusName)
    return FormHistory.create(
        formID=form,
        historyType=historyType,
        createdBy=user,
        createdDate=date.today(),
        status=status,
    )


@pytest.mark.integration
def test_getDepartmentAllocationSummary_no_allocation():
    """
    Test that a department with no Allocation rows gets a zeroed-out summary
    with term=None, instead of an error.
    """
    with mainDB.atomic() as transaction:
        dept = Department.create(departmentID=200, DEPT_NAME="Physics", ACCOUNT="6750", ORG="2120", isActive=True)

        summary = getDepartmentAllocationSummary(dept)

        assert summary["term"] is None
        assert summary["allocated"] == 0
        assert summary["used"] == 0
        assert summary["break_hours"] == 0
        assert summary["used_positions"] == {
            "used_10": 0,
            "used_12": 0,
            "used_15": 0,
            "used_20": 0,
            "used_5_sec": 0,
            "used_10_sec": 0,
        }

        transaction.rollback()


@pytest.mark.integration
def test_getDepartmentAllocationSummary_uses_most_recent_term():
    """
    Test that when a department has allocations across multiple terms, the
    summary reflects only the most recent term's data.
    """
    with mainDB.atomic() as transaction:
        dept = Department.create(departmentID=201, DEPT_NAME="Chemistry", ACCOUNT="6751", ORG="2121", isActive=True)

        oldTerm = Term.create(termCode=900000, termName="AY Test Old")
        newTerm = Term.create(termCode=900100, termName="AY Test New")

        Allocation.create(
            termCode=oldTerm, department=dept, isFinal=True, justification="old",
            primary_10=1, primary_12=0, primary_15=0, primary_20=0,
            secondary_5=0, secondary_10=0, breakHours=50,
        )
        Allocation.create(
            termCode=newTerm, department=dept, isFinal=True, justification="new",
            primary_10=2, primary_12=3, primary_15=0, primary_20=0,
            secondary_5=1, secondary_10=0, breakHours=100,
        )

        supervisor = Supervisor.create(ID="SUP001", isActive=True)
        student = Student.create(ID="STU001", isActive=True)

        # Under the OLD term - should be excluded from the summary
        LaborStatusForm.create(
            termCode=oldTerm, studentSupervisee=student, supervisor=supervisor, department=dept,
            jobType="Primary", WLS="10", POSN_TITLE="Old Job", POSN_CODE="S001",
            weeklyHours=10, contractHours=None,
        )
        # Under the NEW (most recent) term - should be counted
        newForm = LaborStatusForm.create(
            termCode=newTerm, studentSupervisee=student, supervisor=supervisor, department=dept,
            jobType="Primary", WLS="10", POSN_TITLE="New Job", POSN_CODE="S002",
            weeklyHours=10, contractHours=None,
        )
        _createFormHistory(newForm, "Approved")

        summary = getDepartmentAllocationSummary(dept)

        assert summary["term"].termCode == 900100
        assert summary["allocated"] == 6  # 2 + 3 + 0 + 0 + 1 + 0, from the new term only
        assert summary["used"] == 1       # only the new term's LaborStatusForm counts
        assert summary["used_positions"]["used_10"] == 1
        assert summary["break_hours"] == 0

        transaction.rollback()


@pytest.mark.integration
def test_getDepartmentAllocationSummary_break_hours():
    """
    Test that break_hours only sums approved forms with contractHours set
    (break-term contracts), and that those forms are excluded from the
    weekly "used" count.
    """
    with mainDB.atomic() as transaction:
        dept = Department.create(departmentID=202, DEPT_NAME="Biology", ACCOUNT="6752", ORG="2122", isActive=True)
        term = Term.create(termCode=900200, termName="AY Test Break")

        Allocation.create(
            termCode=term, department=dept, isFinal=True, justification="test",
            primary_10=1, primary_12=0, primary_15=0, primary_20=0,
            secondary_5=0, secondary_10=0, breakHours=200,
        )

        supervisor = Supervisor.create(ID="SUP002", isActive=True)
        student = Student.create(ID="STU002", isActive=True)

        breakForm = LaborStatusForm.create(
            termCode=term, studentSupervisee=student, supervisor=supervisor, department=dept,
            jobType="Primary", WLS="10", POSN_TITLE="Break Worker", POSN_CODE="S003",
            weeklyHours=None, contractHours=40,
        )
        _createFormHistory(breakForm, "Approved")

        summary = getDepartmentAllocationSummary(dept)

        assert summary["break_hours"] == 40
        assert summary["used"] == 0

        transaction.rollback()


@pytest.mark.integration
def test_getDepartmentAllocationSummary_department_none():
    """
    Test that passing department=None (e.g. when Department.get() fails in
    the departmentPortal route) returns the zeroed-out fallback instead of
    raising an error.
    """
    summary = getDepartmentAllocationSummary(None)

    assert summary["term"] is None
    assert summary["allocated"] == 0
    assert summary["used"] == 0
    assert summary["break_hours"] == 0
    assert summary["used_positions"] == {
        "used_10": 0,
        "used_12": 0,
        "used_15": 0,
        "used_20": 0,
        "used_5_sec": 0,
        "used_10_sec": 0,
    }


@pytest.mark.integration
def test_getDepartmentAllocationSummary_multiple_allocations_same_term():
    """
    Test that if a department has more than one Allocation row for the same
    most-recent term (e.g. a draft and a final revision, which the model's
    (termCode, department, isFinal) index allows), the totals sum across
    both rows rather than picking just one.
    """
    with mainDB.atomic() as transaction:
        dept = Department.create(departmentID=203, DEPT_NAME="Mathematics", ACCOUNT="6753", ORG="2123", isActive=True)
        term = Term.create(termCode=900300, termName="AY Test Multi")

        Allocation.create(
            termCode=term, department=dept, isFinal=False, justification="draft",
            primary_10=1, primary_12=0, primary_15=0, primary_20=0,
            secondary_5=0, secondary_10=0, breakHours=10,
        )
        Allocation.create(
            termCode=term, department=dept, isFinal=True, justification="final",
            primary_10=2, primary_12=0, primary_15=0, primary_20=0,
            secondary_5=0, secondary_10=0, breakHours=20,
        )

        summary = getDepartmentAllocationSummary(dept)

        assert summary["term"].termCode == 900300
        assert summary["allocated"] == 3  # 1 + 2, summed across both rows

        transaction.rollback()


@pytest.mark.integration
def test_getDepartmentAllocationSummary_allocation_no_labor_status_forms():
    """
    Test that a department with an allocation for the most recent term but no
    LaborStatusForm records at all shows allocated > 0 with used/break_hours
    at 0, rather than erroring on an empty result set.
    """
    with mainDB.atomic() as transaction:
        dept = Department.create(departmentID=204, DEPT_NAME="History", ACCOUNT="6754", ORG="2124", isActive=True)
        term = Term.create(termCode=900400, termName="AY Test Empty")

        Allocation.create(
            termCode=term, department=dept, isFinal=True, justification="test",
            primary_10=3, primary_12=2, primary_15=0, primary_20=0,
            secondary_5=1, secondary_10=0, breakHours=150,
        )

        summary = getDepartmentAllocationSummary(dept)

        assert summary["term"].termCode == 900400
        assert summary["allocated"] == 6
        assert summary["used"] == 0
        assert summary["break_hours"] == 0
        assert summary["used_positions"] == {
            "used_10": 0,
            "used_12": 0,
            "used_15": 0,
            "used_20": 0,
            "used_5_sec": 0,
            "used_10_sec": 0,
        }

        transaction.rollback()


@pytest.mark.integration
def test_countWorkers():
    """
    Test that countWorkers only counts LaborStatusForm rows matching the
    given department, term, job type, and weekly-hours bucket, and excludes
    forms with a different job type/hours bucket, a break-term contract
    (contractHours set instead of weeklyHours), or a denied history status.
    """
    with mainDB.atomic() as transaction:
        dept = Department.create(departmentID=205, DEPT_NAME="English", ACCOUNT="6755", ORG="2125", isActive=True)
        term = Term.create(termCode=900500, termName="AY Test Workers")

        supervisor = Supervisor.create(ID="SUP003", isActive=True)
        student = Student.create(ID="STU003", isActive=True)

        # Matches department, term, job type, and hours bucket - should count
        matchForm = LaborStatusForm.create(
            termCode=term, studentSupervisee=student, supervisor=supervisor, department=dept,
            jobType="Primary", WLS="10", POSN_TITLE="Match", POSN_CODE="S010",
            weeklyHours=10, contractHours=None,
        )
        _createFormHistory(matchForm, "Approved")

        # Different job type - should not count toward ("Primary", 10)
        wrongJobTypeForm = LaborStatusForm.create(
            termCode=term, studentSupervisee=student, supervisor=supervisor, department=dept,
            jobType="Secondary", WLS="10", POSN_TITLE="Wrong Job Type", POSN_CODE="S011",
            weeklyHours=10, contractHours=None,
        )
        _createFormHistory(wrongJobTypeForm, "Approved")

        # Different hours bucket - should not count toward ("Primary", 10)
        wrongHoursForm = LaborStatusForm.create(
            termCode=term, studentSupervisee=student, supervisor=supervisor, department=dept,
            jobType="Primary", WLS="12", POSN_TITLE="Wrong Hours", POSN_CODE="S012",
            weeklyHours=12, contractHours=None,
        )
        _createFormHistory(wrongHoursForm, "Approved")

        # Break-term contract (contractHours set) - should not count even though
        # job type and weeklyHours otherwise match
        breakContractForm = LaborStatusForm.create(
            termCode=term, studentSupervisee=student, supervisor=supervisor, department=dept,
            jobType="Primary", WLS="10", POSN_TITLE="Break Contract", POSN_CODE="S013",
            weeklyHours=10, contractHours=40,
        )
        _createFormHistory(breakContractForm, "Approved")

        # Matches everything but was DENIED - should not count
        deniedForm = LaborStatusForm.create(
            termCode=term, studentSupervisee=student, supervisor=supervisor, department=dept,
            jobType="Primary", WLS="10", POSN_TITLE="Denied Match", POSN_CODE="S014",
            weeklyHours=10, contractHours=None,
        )
        _createFormHistory(deniedForm, "Denied by Admin")

        assert countWorkers(dept, term.termCode, "Primary", 10) == 1
        assert countWorkers(dept, term.termCode, "Secondary", 10) == 1
        assert countWorkers(dept, term.termCode, "Primary", 12) == 1
        assert countWorkers(dept, term.termCode, "Primary", 15) == 0

        transaction.rollback()


@pytest.mark.integration
def test_getBreakHours():
    """
    Test that getBreakHours sums only APPROVED forms with contractHours set
    (break-term contracts) for the given department and term, excludes
    weekly-hours forms, excludes forms under a different term, and excludes
    forms that are not approved (e.g. still pending).
    """
    with mainDB.atomic() as transaction:
        dept = Department.create(departmentID=206, DEPT_NAME="Philosophy", ACCOUNT="6756", ORG="2126", isActive=True)
        term = Term.create(termCode=900600, termName="AY Test Break Hours")
        otherTerm = Term.create(termCode=900601, termName="AY Test Other Term")

        supervisor = Supervisor.create(ID="SUP004", isActive=True)
        student = Student.create(ID="STU004", isActive=True)

        # Approved break-term contracts under the target term - should be summed
        formA = LaborStatusForm.create(
            termCode=term, studentSupervisee=student, supervisor=supervisor, department=dept,
            jobType="Primary", WLS="10", POSN_TITLE="Break A", POSN_CODE="S020",
            weeklyHours=None, contractHours=40,
        )
        _createFormHistory(formA, "Approved")

        formB = LaborStatusForm.create(
            termCode=term, studentSupervisee=student, supervisor=supervisor, department=dept,
            jobType="Secondary", WLS="5", POSN_TITLE="Break B", POSN_CODE="S021",
            weeklyHours=None, contractHours=60,
        )
        _createFormHistory(formB, "Approved")

        # Weekly-hours form (contractHours=None) - should be excluded regardless
        formC = LaborStatusForm.create(
            termCode=term, studentSupervisee=student, supervisor=supervisor, department=dept,
            jobType="Primary", WLS="10", POSN_TITLE="Weekly Job", POSN_CODE="S022",
            weeklyHours=10, contractHours=None,
        )
        _createFormHistory(formC, "Approved")

        # Break-term contract under a DIFFERENT term - should be excluded
        formD = LaborStatusForm.create(
            termCode=otherTerm, studentSupervisee=student, supervisor=supervisor, department=dept,
            jobType="Primary", WLS="10", POSN_TITLE="Break Other Term", POSN_CODE="S023",
            weeklyHours=None, contractHours=100,
        )
        _createFormHistory(formD, "Approved")

        # Break-term contract that is still PENDING - should be excluded
        formE = LaborStatusForm.create(
            termCode=term, studentSupervisee=student, supervisor=supervisor, department=dept,
            jobType="Primary", WLS="10", POSN_TITLE="Break Pending", POSN_CODE="S024",
            weeklyHours=None, contractHours=999,
        )
        _createFormHistory(formE, "Pending")

        assert getBreakHours(dept, term.termCode) == 100  # 40 + 60, excludes the pending form
        assert getBreakHours(dept, otherTerm.termCode) == 100

        transaction.rollback()
