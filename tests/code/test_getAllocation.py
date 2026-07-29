import pytest
from app.models import mainDB
from app.models.department import Department
from app.models.term import Term
from app.models.allocation import Allocation
from app.models.laborStatusForm import LaborStatusForm
from app.models.student import Student
from app.models.supervisor import Supervisor
from app.logic.getAllocation import getDepartmentAllocationSummary


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
        LaborStatusForm.create(
            termCode=newTerm, studentSupervisee=student, supervisor=supervisor, department=dept,
            jobType="Primary", WLS="10", POSN_TITLE="New Job", POSN_CODE="S002",
            weeklyHours=10, contractHours=None,
        )

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
    Test that break_hours only sums forms with contractHours set (break-term
    contracts), and that those forms are excluded from the weekly "used" count.
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

        LaborStatusForm.create(
            termCode=term, studentSupervisee=student, supervisor=supervisor, department=dept,
            jobType="Primary", WLS="10", POSN_TITLE="Break Worker", POSN_CODE="S003",
            weeklyHours=None, contractHours=40,
        )

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
