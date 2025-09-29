import pytest

from app.models import mainDB
from app.logic.allPendingForms import modal_approval_and_denial_data
from app.models.formHistory import FormHistory

@pytest.mark.integration
def test_pendingApprovalModal():
    with mainDB.atomic() as transaction:
        # TODO create an adjustment form to test with

        fhList = FormHistory.select(FormHistory.formHistoryID).where(FormHistory.formHistoryID.in_([2,3]))
        targetData = [
                    ['Alex Bryant','Computer Science','Student Programmer', '10', 'None', 'Scott Heggen'],
                    ['Test Taker','Labor Department','Labor Workers', '10', 'None', 'Scott Heggen'],
                ]
        assert targetData == modal_approval_and_denial_data([fh.formHistoryID for fh in fhList])

        transaction.rollback()


