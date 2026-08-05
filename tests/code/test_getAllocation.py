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
from app.logic.getAllocation import getDepartmentAllocationSummary, getCurrentSemesterLabel


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
    in one term (draft and final both counted), break-term contracts, an
    allocation with no forms, and a most-recent term that only has a draft
    (not yet final) allocation.

    "used"/"usedPositions"/"breakHours" are sourced from allocationManager's
    getContractedAllocations (see test_allocationManger.py for that
    function's own unit coverage) - only the term-selection and allocated-sum
    behavior is re-verified here. "allocated" is summed directly from the
    Allocation rows for the most recent term (both draft and final), not
    routed through allocationManager, since a department's allocation is
    often still a draft when this is viewed.
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

        # A most-recent term with only a draft (isFinal=False) allocation - no
        # final row exists yet - still reports the draft's own numbers rather
        # than zeroing out, since a department's allocation is often still a
        # draft before it's finalized
        draftOnlyDept = Department.create(departmentID=205, DEPT_NAME="Art", ACCOUNT="6755", ORG="2125", isActive=True)
        draftOnlyTerm = Term.create(termCode=900500, termName="AY Test Draft Only")

        Allocation.create(
            termCode=draftOnlyTerm, department=draftOnlyDept, isFinal=False, justification="draft",
            primary_10=5, primary_12=0, primary_15=0, primary_20=0,
            secondary_5=0, secondary_10=0, breakHours=30,
        )

        summary = getDepartmentAllocationSummary(draftOnlyDept)

        assert summary["term"].termCode == 900500
        assert summary["allocated"] == 5
        assert summary["used"] == 0
        assert summary["breakHours"] == 0
        assert summary["usedPositions"] == zeroedUsedPositions

        transaction.rollback()


# countWorkers and getBreakHours were removed in favor of calling
# allocationManager's getContractedAllocations directly from
# getDepartmentAllocationSummary (see test_allocationManger.py's
# test_countContracts/test_getContractedAllocations for that function's own
# coverage). Note the counting rules aren't identical to the old
# countWorkers/getBreakHours: getContractedAllocations doesn't exclude
# break-term contracts (contractHours set) from the weekly-hours buckets, and
# uses a narrower status whitelist instead of "anything not Denied".
