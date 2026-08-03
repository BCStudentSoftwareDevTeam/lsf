import io

import pytest

from app.logic.download import makePositionDescriptionPDF
from app.models import mainDB
from app.models.department import Department
from app.models.positionHistory import PositionHistory
from app.models.positionDescriptionSection import PositionDescriptionSection

@pytest.mark.integration
def test_makePositionDescriptionPDF():
    """
    Tests that makePositionDescriptionPDF generates valid PDF buffers
    for positions with and without description sections.
    """
    with mainDB.atomic() as transaction:

        # Create the department used by all positions in the test.
        department = Department.create(
            departmentID=200,
            DEPT_NAME="Physics",
            ACCOUNT="6742",
            ORG="2116",
            departmentCompliance=True,
            isActive=True,
        )

        # Create a position that will have description sections.
        positionWithSections = PositionHistory.create(
            positionTitle="Lab Technician",
            positionCode="S34516",
            department=department,
            status="Active",
            wls=3,
            revisionDate="2023-01-01",
            revisedBy="Jane Doe",
        )

        # Create a position that will not have description sections.
        positionWithoutSections = PositionHistory.create(
            positionTitle="Research Assistant",
            positionCode="S34517",
            department=department,
            status="Active",
            wls=2,
            revisionDate="2023-01-02",
            revisedBy="Sarah Smith",
        )

        # Create sections for the first position. Insertion is out of order in order to test the section query's ordering logic is applied when the PDF is generated.
        PositionDescriptionSection.create(
            position=positionWithSections,
            sectionTitle="Responsibilities",
            sectionContent="Supports experiments and records results.",
            order=2,
        )

        PositionDescriptionSection.create(
            position=positionWithSections,
            sectionTitle="Position Summary",
            sectionContent="Maintains laboratory equipment.",
            order=1,
        )

        # Generate a PDF for the position that has description sections.
        pdfBufferWithSections = makePositionDescriptionPDF(
            department,
            positionWithSections,
        )

        # Verify that the result is a nonempty BytesIO containing a PDF.
        assert isinstance(pdfBufferWithSections, io.BytesIO)

        pdfBytesWithSections = pdfBufferWithSections.getvalue()

        assert len(pdfBytesWithSections) > 0
        assert pdfBytesWithSections.startswith(b"%PDF-")
        assert pdfBytesWithSections.rstrip().endswith(b"%%EOF")

        # Generate a PDF for the position without description sections. This exercises the "No description available." branch.
        pdfBufferWithoutSections = makePositionDescriptionPDF(
            department,
            positionWithoutSections,
        )

        # Verify that the second result is also a valid PDF buffer.
        assert isinstance(pdfBufferWithoutSections, io.BytesIO)

        pdfBytesWithoutSections = pdfBufferWithoutSections.getvalue()

        assert len(pdfBytesWithoutSections) > 0
        assert pdfBytesWithoutSections.startswith(b"%PDF-")
        assert pdfBytesWithoutSections.rstrip().endswith(b"%%EOF")

        # Verify that the two different positions produce different PDFs.
        assert pdfBytesWithSections != pdfBytesWithoutSections

        # Roll back all database records created by this test.
        transaction.rollback()