import pytest
from app.models import mainDB
from app.models.term import Term
from app.models.department import Department
from app.models.allocation import Allocation
from app.models.formHistory import FormHistory
from app.logic.allocation import getAllocationWarning


@pytest.mark.integration
def test_getAllocationWarning_returnsNoneWithoutAnAllocationRow():
    with mainDB.atomic() as transaction:
        dept = Department.get_by_id(1)  # Computer Science
        term = Term.get_by_id(202000)   # no Allocation row exists for this department/term in demo data

        assert getAllocationWarning(dept, term) is None

        transaction.rollback()


@pytest.mark.integration
def test_getAllocationWarning_underAllocated():
    with mainDB.atomic() as transaction:
        dept = Department.get_by_id(1)
        term = Term.get_by_id(202000)
        Allocation.create(termCode=term, department=dept, isFinal=True, justification="test",
                           primary_10=5, primary_12=5, primary_15=5, primary_20=5,
                           secondary_5=5, secondary_10=5, breakHours=100)

        warning = getAllocationWarning(dept, term)

        assert warning["totalPositionsUsed"] == 1  # formHistoryID 2: a pending 10hr Primary LSF for this dept/term
        assert warning["positionsRemaining"] == 29
        assert warning["overAllocatedBands"] == []
        assert warning["isPositionsOverAllocated"] is False
        assert warning["isBreakHoursOverAllocated"] is False
        assert warning["isOverAllocated"] is False

        transaction.rollback()


@pytest.mark.integration
def test_getAllocationWarning_overOnSingleBandOnlyIsStillFlagged():
    """
    Regression test for the fix in 035cda02: a department can be within its
    aggregate position total while still exceeding one specific hour-band, so
    each band has to be checked individually rather than only the aggregate.
    """
    with mainDB.atomic() as transaction:
        dept = Department.get_by_id(1)
        term = Term.get_by_id(202000)
        Allocation.create(termCode=term, department=dept, isFinal=True, justification="test",
                           primary_10=0, primary_12=10, primary_15=10, primary_20=10,
                           secondary_5=10, secondary_10=10, breakHours=100)

        warning = getAllocationWarning(dept, term)

        assert warning["positionsRemaining"] > 0  # fine in aggregate...
        assert warning["overAllocatedBands"] == [{"label": "10 Hour Primary", "used": 1, "allocated": 0}]
        assert warning["isPositionsOverAllocated"] is True  # ...but flagged for the one over band
        assert warning["isOverAllocated"] is True

        transaction.rollback()


@pytest.mark.integration
def test_getAllocationWarning_overOnAggregatePositions():
    with mainDB.atomic() as transaction:
        dept = Department.get_by_id(1)
        term = Term.get_by_id(202000)
        Allocation.create(termCode=term, department=dept, isFinal=True, justification="test",
                           primary_10=0, primary_12=0, primary_15=0, primary_20=0,
                           secondary_5=0, secondary_10=0, breakHours=100)

        warning = getAllocationWarning(dept, term)

        assert warning["positionsRemaining"] == -1
        assert warning["isPositionsOverAllocated"] is True
        assert warning["isOverAllocated"] is True

        transaction.rollback()


@pytest.mark.integration
def test_getAllocationWarning_overOnBreakHours():
    with mainDB.atomic() as transaction:
        dept = Department.get_by_id(1)  # Computer Science already has a 202400 Allocation (breakHours=550)
        term = Term.get_by_id(202400)

        # Temporarily move an existing LSF into a break term sharing the 2024 academic year
        # prefix, with contractHours pushing the department over its break hour allocation.
        fh = FormHistory.get(FormHistory.formHistoryID == 2)
        lsf = fh.formID
        lsf.termCode = Term.get_by_id(202401)  # Thanksgiving Break 2024
        lsf.contractHours = 600
        lsf.save()

        warning = getAllocationWarning(dept, term)

        assert warning["breakHoursAllocated"] == 550
        assert warning["breakHoursUsed"] == 600
        assert warning["breakHoursRemaining"] == -50
        assert warning["isBreakHoursOverAllocated"] is True
        assert warning["isOverAllocated"] is True

        transaction.rollback()
