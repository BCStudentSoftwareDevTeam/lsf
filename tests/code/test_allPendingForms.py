import pytest

from app.models import mainDB
from app.models.allocation import Allocation
from app.logic.allPendingForms import modal_approval_and_denial_data
from app.models.formHistory import FormHistory

@pytest.mark.integration
def test_pendingApprovalModal():
    with mainDB.atomic() as transaction:
        # TODO create an adjustment form to test with

        fhList = FormHistory.select().where(FormHistory.formHistoryID.in_([2,3]))
        fhIDs = [fh.formHistoryID for fh in fhList]
        targetDetails = [
                    ['Alex Bryant','Computer Science','Student Programmer', '10', 'None', 'Scott Heggen'],
                    ['Test Taker','Labor Department','Labor Workers', '10', 'None', 'Scott Heggen'],
                ]

      
        departments = [fh.formID.department for fh in fhList]
        Allocation.delete().where(Allocation.department.in_(departments)).execute()

        result = modal_approval_and_denial_data(fhIDs)
        assert result["details"] == targetDetails
        assert result["allocationWarnings"] == []

        lsf = FormHistory.get_by_id(2).formID
        Allocation.create(termCode       = lsf.termCode,
                          department     = lsf.department,
                          isFinal        = True,
                          justification  = "test",
                          primary_10     = 1,
                          primary_12     = 0,
                          primary_15     = 0,
                          primary_20     = 0,
                          secondary_5    = 0,
                          secondary_10   = 0,
                          breakHours     = 0)

        result = modal_approval_and_denial_data(fhIDs)
        assert result["details"] == targetDetails
        assert [w['departmentName'] for w in result["allocationWarnings"]] == ['Computer Science']
        assert result["allocationWarnings"][0]['totalPositionsAllocated'] == 1

        transaction.rollback()
