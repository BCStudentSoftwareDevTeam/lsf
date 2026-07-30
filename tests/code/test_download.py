import io
from flask import g
from fpdf import FPDF
import pytest
from app.models import mainDB

from app.logic.download import makePositionDescriptionPDF
from app.models.department import Department
from app.models.positionHistory import PositionHistory


def test_makePositionDescriptionPDF():
    with mainDB.atomic() as transaction:
        dept = Department.create(departmentID=200, DEPT_NAME="Physics", ACCOUNT="6742", ORG="2116", departmentCompliance=True, isActive=True)

        position = PositionHistory.create(positionTitle="Lab Technician",
                                           positionCode="S34516",
                                           department=dept,
                                           status="Active",
                                           wls=3,
                                           revisionDate="2023-01-01",
                                           revisedBy="Jane Doe",
                                           description="This is a test position description.")

        pdf_buffer = makePositionDescriptionPDF(dept, position)

        assert isinstance(pdf_buffer, io.BytesIO)

        pdf_bytes = pdf_buffer.getvalue()
        assert len(pdf_bytes) > 0
        assert pdf_bytes[:5] == b'%PDF-'

        transaction.rollback()