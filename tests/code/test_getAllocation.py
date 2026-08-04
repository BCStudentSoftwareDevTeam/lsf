from datetime import date
from unittest.mock import patch

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
from app.logic.getAllocation import getDepartmentAllocationSummary, countWorkers, getBreakHours, getCurrentSemesterLabel


def createFormHistory(form, statusName):
    """Attach a "Labor Status Form" history entry with the given status, since
    the allocation queries only count forms that have one."""
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


@pytest.mark.unit
def test_getCurrentSemesterLabel():
    """
    Test that a term maps to the Fall/Spring label for whichever half of the
    academic year today falls in, and that a missing term has no label.
    """
    # No term (e.g. a department with no allocations) - nothing to label
    assert getCurrentSemesterLabel(None) is None

    term = Term(termCode=202500)

    # Aug-Dec half of the academic year - reads as Fall of the term's own year
    with patch("app.logic.getAllocation.date") as mockDate:
        mockDate.today.return_value = date(2025, 9, 15)
        assert getCurrentSemesterLabel(term) == "Fall 2025"

    # Jan-Jul half of the same academic-year term - reads as Spring of the next year
    with patch("app.logic.getAllocation.date") as mockDate:
        mockDate.today.return_value = date(2026, 2, 10)
        assert getCurrentSemesterLabel(term) == "Spring 2026"


@pytest.mark.integration
def test_getDepartmentAllocationSummary():
    """
    Test that the summary reports allocated/used/breakHours for a department's
    most recent term, covering a missing department, a department with no
    Allocation rows, allocations spread across terms, several Allocation rows
    in one term, break-term contracts, and an allocation with no forms.
    """
    zeroedUsedPositions = {
        "used10": 0,
        "used12": 0,
        "used15": 0,
        "used20": 0,
        "usedSecondary5": 0,
        "usedSecondary10": 0,
    }

    # department=None (e.g. when Department.get() fails in the departmentPortal
    # route) returns the zeroed-out fallback instead of raising an error
    summary = getDepartmentAllocationSummary(None)

    assert summary["term"] is None
    assert summary["allocated"] == 0
    assert summary["used"] == 0
    assert summary["breakHours"] == 0
    assert summary["usedPositions"] == zeroedUsedPositions

    with mainDB.atomic() as transaction:
        # A department with no Allocation rows gets the same zeroed-out summary
        # with term=None
        emptyDept = Department.create(departmentID=200, DEPT_NAME="Physics", ACCOUNT="6750", ORG="2120", isActive=True)

        summary = getDepartmentAllocationSummary(emptyDept)

        assert summary["term"] is None
        assert summary["allocated"] == 0
        assert summary["used"] == 0
        assert summary["breakHours"] == 0
        assert summary["usedPositions"] == zeroedUsedPositions

        # With allocations across multiple terms, the summary reflects only the
        # most recent term's data
        multiTermDept = Department.create(departmentID=201, DEPT_NAME="Chemistry", ACCOUNT="6751", ORG="2121", isActive=True)

        oldTerm = Term.create(termCode=900000, termName="AY Test Old")
        newTerm = Term.create(termCode=900100, termName="AY Test New")

        Allocation.create(
            termCode=oldTerm, department=multiTermDept, isFinal=True, justification="old",
            primary_10=1, primary_12=0, primary_15=0, primary_20=0,
            secondary_5=0, secondary_10=0, breakHours=50,
        )
        Allocation.create(
            termCode=newTerm, department=multiTermDept, isFinal=True, justification="new",
            primary_10=2, primary_12=3, primary_15=0, primary_20=0,
            secondary_5=1, secondary_10=0, breakHours=100,
        )

        supervisor = Supervisor.create(ID="SUP001", isActive=True)
        student = Student.create(ID="STU001", isActive=True)

        # Approved under the OLD term - excluded by the term filter alone
        oldForm = LaborStatusForm.create(
            termCode=oldTerm, studentSupervisee=student, supervisor=supervisor, department=multiTermDept,
            jobType="Primary", WLS="10", POSN_TITLE="Old Job", POSN_CODE="S001",
            weeklyHours=10, contractHours=None,
        )
        createFormHistory(oldForm, "Approved")

        # Under the NEW (most recent) term - should be counted
        newForm = LaborStatusForm.create(
            termCode=newTerm, studentSupervisee=student, supervisor=supervisor, department=multiTermDept,
            jobType="Primary", WLS="10", POSN_TITLE="New Job", POSN_CODE="S002",
            weeklyHours=10, contractHours=None,
        )
        createFormHistory(newForm, "Approved")

        # Denied under the NEW term - should not count toward used
        deniedForm = LaborStatusForm.create(
            termCode=newTerm, studentSupervisee=student, supervisor=supervisor, department=multiTermDept,
            jobType="Primary", WLS="12", POSN_TITLE="Denied Job", POSN_CODE="S004",
            weeklyHours=12, contractHours=None,
        )
        createFormHistory(deniedForm, "Denied by Admin")

        summary = getDepartmentAllocationSummary(multiTermDept)

        assert summary["term"].termCode == 900100
        assert summary["allocated"] == 6  # 2 + 3 + 0 + 0 + 1 + 0, from the new term only
        assert summary["used"] == 1       # only the new term's approved LaborStatusForm counts
        assert summary["usedPositions"]["used10"] == 1
        assert summary["usedPositions"]["used12"] == 0  # the denied form is not counted
        assert summary["breakHours"] == 0

        # breakHours only sums approved forms with contractHours set (break-term
        # contracts), and those forms are excluded from the weekly "used" count
        breakDept = Department.create(departmentID=202, DEPT_NAME="Biology", ACCOUNT="6752", ORG="2122", isActive=True)
        breakTerm = Term.create(termCode=900200, termName="AY Test Break")

        Allocation.create(
            termCode=breakTerm, department=breakDept, isFinal=True, justification="test",
            primary_10=1, primary_12=0, primary_15=0, primary_20=0,
            secondary_5=0, secondary_10=0, breakHours=200,
        )

        breakSupervisor = Supervisor.create(ID="SUP002", isActive=True)
        breakStudent = Student.create(ID="STU002", isActive=True)

        breakForm = LaborStatusForm.create(
            termCode=breakTerm, studentSupervisee=breakStudent, supervisor=breakSupervisor, department=breakDept,
            jobType="Primary", WLS="10", POSN_TITLE="Break Worker", POSN_CODE="S003",
            weeklyHours=None, contractHours=40,
        )
        createFormHistory(breakForm, "Approved")

        summary = getDepartmentAllocationSummary(breakDept)

        assert summary["breakHours"] == 40
        assert summary["used"] == 0

        # More than one Allocation row for the same most-recent term (e.g. a
        # draft and a final revision, which the model's (termCode, department,
        # isFinal) index allows) sums across both rows rather than picking one
        multiRowDept = Department.create(departmentID=203, DEPT_NAME="Mathematics", ACCOUNT="6753", ORG="2123", isActive=True)
        multiRowTerm = Term.create(termCode=900300, termName="AY Test Multi")

        Allocation.create(
            termCode=multiRowTerm, department=multiRowDept, isFinal=False, justification="draft",
            primary_10=1, primary_12=0, primary_15=0, primary_20=0,
            secondary_5=0, secondary_10=0, breakHours=10,
        )
        Allocation.create(
            termCode=multiRowTerm, department=multiRowDept, isFinal=True, justification="final",
            primary_10=2, primary_12=0, primary_15=0, primary_20=0,
            secondary_5=0, secondary_10=0, breakHours=20,
        )

        summary = getDepartmentAllocationSummary(multiRowDept)

        assert summary["term"].termCode == 900300
        assert summary["allocated"] == 3  # 1 + 2, summed across both rows

        # An allocation for the most recent term with no LaborStatusForm records
        # at all shows allocated > 0 with used/breakHours at 0, rather than
        # erroring on an empty result set
        noFormsDept = Department.create(departmentID=204, DEPT_NAME="History", ACCOUNT="6754", ORG="2124", isActive=True)
        noFormsTerm = Term.create(termCode=900400, termName="AY Test Empty")

        Allocation.create(
            termCode=noFormsTerm, department=noFormsDept, isFinal=True, justification="test",
            primary_10=3, primary_12=2, primary_15=0, primary_20=0,
            secondary_5=1, secondary_10=0, breakHours=150,
        )

        summary = getDepartmentAllocationSummary(noFormsDept)

        assert summary["term"].termCode == 900400
        assert summary["allocated"] == 6
        assert summary["used"] == 0
        assert summary["breakHours"] == 0
        assert summary["usedPositions"] == zeroedUsedPositions

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
        createFormHistory(matchForm, "Approved")

        # Different job type - should not count toward ("Primary", 10)
        wrongJobTypeForm = LaborStatusForm.create(
            termCode=term, studentSupervisee=student, supervisor=supervisor, department=dept,
            jobType="Secondary", WLS="10", POSN_TITLE="Wrong Job Type", POSN_CODE="S011",
            weeklyHours=10, contractHours=None,
        )
        createFormHistory(wrongJobTypeForm, "Approved")

        # Different hours bucket - should not count toward ("Primary", 10)
        wrongHoursForm = LaborStatusForm.create(
            termCode=term, studentSupervisee=student, supervisor=supervisor, department=dept,
            jobType="Primary", WLS="12", POSN_TITLE="Wrong Hours", POSN_CODE="S012",
            weeklyHours=12, contractHours=None,
        )
        createFormHistory(wrongHoursForm, "Approved")

        # Break-term contract (contractHours set) - should not count even though
        # job type and weeklyHours otherwise match
        breakContractForm = LaborStatusForm.create(
            termCode=term, studentSupervisee=student, supervisor=supervisor, department=dept,
            jobType="Primary", WLS="10", POSN_TITLE="Break Contract", POSN_CODE="S013",
            weeklyHours=10, contractHours=40,
        )
        createFormHistory(breakContractForm, "Approved")

        # Matches everything but was DENIED - should not count
        deniedForm = LaborStatusForm.create(
            termCode=term, studentSupervisee=student, supervisor=supervisor, department=dept,
            jobType="Primary", WLS="10", POSN_TITLE="Denied Match", POSN_CODE="S014",
            weeklyHours=10, contractHours=None,
        )
        createFormHistory(deniedForm, "Denied by Admin")

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
        createFormHistory(formA, "Approved")

        formB = LaborStatusForm.create(
            termCode=term, studentSupervisee=student, supervisor=supervisor, department=dept,
            jobType="Secondary", WLS="5", POSN_TITLE="Break B", POSN_CODE="S021",
            weeklyHours=None, contractHours=60,
        )
        createFormHistory(formB, "Approved")

        # Weekly-hours form (contractHours=None) - should be excluded regardless
        formC = LaborStatusForm.create(
            termCode=term, studentSupervisee=student, supervisor=supervisor, department=dept,
            jobType="Primary", WLS="10", POSN_TITLE="Weekly Job", POSN_CODE="S022",
            weeklyHours=10, contractHours=None,
        )
        createFormHistory(formC, "Approved")

        # Break-term contract under a DIFFERENT term - should be excluded
        formD = LaborStatusForm.create(
            termCode=otherTerm, studentSupervisee=student, supervisor=supervisor, department=dept,
            jobType="Primary", WLS="10", POSN_TITLE="Break Other Term", POSN_CODE="S023",
            weeklyHours=None, contractHours=25,
        )
        createFormHistory(formD, "Approved")

        # Break-term contract that is still PENDING - should be excluded
        formE = LaborStatusForm.create(
            termCode=term, studentSupervisee=student, supervisor=supervisor, department=dept,
            jobType="Primary", WLS="10", POSN_TITLE="Break Pending", POSN_CODE="S024",
            weeklyHours=None, contractHours=999,
        )
        createFormHistory(formE, "Pending")

        assert getBreakHours(dept, term.termCode) == 100       # 40 + 60, excludes the pending form
        assert getBreakHours(dept, otherTerm.termCode) == 25   # only the other term's contract

        transaction.rollback()
