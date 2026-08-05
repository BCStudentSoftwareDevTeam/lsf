import io

import pytest

from app.logic.download import makePositionDescriptionPDF, removeHTML
from app.models import mainDB
from app.models.department import Department
from app.models.positionDescriptionSection import PositionDescriptionSection
from app.models.positionHistory import PositionHistory


@pytest.mark.integration
def test_makePositionDescriptionPDF():
    """
    Tests both HTML stripping and PDF generation using the makePositionDescriptionPDF() function.
    """
    with mainDB.atomic() as transaction:
        headingResult = removeHTML(
            "<h3>Learning Opportunities</h3>"
        )

        # Confirm that the heading text remains.
        assert "Learning Opportunities" in headingResult

        # Confirm that the HTML tags were removed.
        assert "<h3>" not in headingResult
        assert "</h3>" not in headingResult

        sectionResult = removeHTML(
            """
            <h4>A. Equipment Management</h4>
            <p>Maintains laboratory equipment &amp; supplies.</p>

            <h4>B. Experiment Support</h4>
            <p>Supports experiments and records results.</p>
            """
        )

        # Normalize whitespace so the test does not depend on the exact number of newlines produced by removeHTML().
        normalizedSectionResult = " ".join(sectionResult.split())

        # Confirm that all readable content remains after stripping HTML.
        assert "A. Equipment Management" in normalizedSectionResult
        assert "Maintains laboratory equipment & supplies." in normalizedSectionResult
        assert "B. Experiment Support" in normalizedSectionResult
        assert "Supports experiments and records results." in normalizedSectionResult

        # Confirm that HTML tags and encoded entities were removed.
        assert "<h4>" not in normalizedSectionResult
        assert "</h4>" not in normalizedSectionResult
        assert "<p>" not in normalizedSectionResult
        assert "</p>" not in normalizedSectionResult
        assert "&amp;" not in normalizedSectionResult

        # Create the department shared by both test positions.
        department = Department.create(
            departmentID=200,
            DEPT_NAME="Physics",
            ACCOUNT="6742",
            ORG="2116",
            departmentCompliance=True,
            isActive=True,
        )

        # Create a position with HTML-formatted description sections.
        positionWithSections = PositionHistory.create(
            positionTitle="<strong>Lab Technician</strong>",
            positionCode="S34516",
            department=department,
            status="Active",
            wls=3,
            revisionDate="2023-01-01",
            revisedBy="Jane Doe",
        )

        # Create a position without description sections to test for "No description available." output.
        positionWithoutSections = PositionHistory.create(
            positionTitle="Research Assistant",
            positionCode="S34517",
            department=department,
            status="Active",
            wls=2,
            revisionDate="2023-01-02",
            revisedBy="Sarah Smith",
        )

        # Insert this section first even though its order is 2. Tests section-ordering logic used by getPositionDescriptionSections().
        PositionDescriptionSection.create(
            position=positionWithSections,
            sectionTitle="<h3>Responsibilities</h3>",
            sectionContent="""
                <h4>A. Equipment Management</h4>
                <p>Maintains laboratory equipment &amp; supplies.</p>

                <h4>B. Experiment Support</h4>
                <p>Supports experiments and records results.</p>
            """,
            order=2,
        )

        # Insert the order-1 section second.
        PositionDescriptionSection.create(
            position=positionWithSections,
            sectionTitle="<h3>Position Summary</h3>",
            sectionContent="""
                <p>Provides support for laboratory research.</p>
                <p>Works with faculty and student researchers.</p>
            """,
            order=1,
        )

        pdfBufferWithSections = makePositionDescriptionPDF(
            department,
            positionWithSections,
        )

        # Confirm that the function returns an in-memory byte buffer.
        assert isinstance(pdfBufferWithSections, io.BytesIO)

        pdfBytesWithSections = pdfBufferWithSections.getvalue()

        # Confirm that the generated PDF is not empty.
        assert len(pdfBytesWithSections) > 0

        # Confirm that the output begins with the standard PDF header.
        assert pdfBytesWithSections.startswith(b"%PDF-")

        # Confirm that the output ends with the standard PDF marker.
        assert pdfBytesWithSections.rstrip().endswith(b"%%EOF")

        pdfBufferWithoutSections = makePositionDescriptionPDF(
            department,
            positionWithoutSections,
        )

        # Confirm that the fallback branch also returns a BytesIO object.
        assert isinstance(pdfBufferWithoutSections, io.BytesIO)

        pdfBytesWithoutSections = pdfBufferWithoutSections.getvalue()

        # Confirm that the fallback PDF is not empty.
        assert len(pdfBytesWithoutSections) > 0

        # Confirm that the fallback output is also a valid PDF.
        assert pdfBytesWithoutSections.startswith(b"%PDF-")
        assert pdfBytesWithoutSections.rstrip().endswith(b"%%EOF")

        # Confirm that the two positions did not produce identical PDFs.
        assert pdfBytesWithSections != pdfBytesWithoutSections

        transaction.rollback()