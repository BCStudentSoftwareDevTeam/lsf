import pytest
from flask import g

from app import app
from app.models import mainDB
from app.logic.allPendingForms import modal_approval_and_denial_data
from app.models.formHistory import FormHistory

@pytest.mark.integration
def test_pendingApprovalModal():
    with mainDB.atomic() as transaction:
        # TODO create an adjustment form to test with

        fhList = FormHistory.select(FormHistory.formHistoryID).where(FormHistory.formHistoryID.in_([2,3]))
        targetDetails = [
                    ['Alex Bryant','Computer Science','Student Programmer', '10', 'None', 'Scott Heggen'],
                    ['Test Taker','Labor Department','Labor Workers', '10', 'None', 'Scott Heggen'],
                ]

        with app.test_request_context():
            g.openTerm = 202000  # neither department has an Allocation row for this term in demo data
            result = modal_approval_and_denial_data([fh.formHistoryID for fh in fhList])

        assert result["details"] == targetDetails
        assert result["allocationWarnings"] == []

        transaction.rollback()


