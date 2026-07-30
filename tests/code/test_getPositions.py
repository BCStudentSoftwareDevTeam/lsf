import pytest
from app.models import mainDB
from app.models.department import Department
from app.models.positionHistory import PositionHistory
from app.logic.getPositions import *
@pytest.mark.integration
def test_getActivePositions():
    """
    Test to check if the getActivePositions function in getPositions.py correctly retrieves active positions for a single department.
    """
    with mainDB.atomic() as transaction:
        dept1 = Department.create(departmentID=100, DEPT_NAME="Computer Science", ACCOUNT="6740", ORG="2114", departmentCompliance=True, isActive=True)
        dept2 = Department.create(departmentID=101, DEPT_NAME="Mathematics", ACCOUNT="6741", ORG="2115", departmentCompliance=True, isActive=True)

        position1 = PositionHistory.create(positionTitle="Teaching Assistant", 
                                            positionCode="S34512", 
                                            department=dept1, 
                                            status="Active", 
                                            wls=4,
                                            revisionDate="2023-01-01", 
                                            description="")
        
        position2 = PositionHistory.create(positionTitle="Research Assistant",
                                            positionCode="S34513",
                                            department=dept1,
                                            status="Inactive",
                                            wls=3,
                                            revisionDate="2023-01-01",
                                            description="")

        position3 = PositionHistory.create(positionTitle="Lab Assistant",
                                            positionCode="S34514",
                                            department=dept1,
                                            status="Active",
                                            wls=2,
                                            revisionDate="2026-01-01",
                                            description="") 

        position4 = PositionHistory.create(positionTitle="Intern",
                                            positionCode="S34515",
                                            department=dept1,
                                            status="Active",
                                            wls=1,
                                            revisionDate="2023-01-01",
                                            description="")

        positionsList1, posURL1 = getActivePositions(dept1)
        positionsList2, posURL2 = getActivePositions(dept2)
        positionsList3, posURL3 = getActivePositions(None)



        # Check that only active positions are returned
        assert len(positionsList1) == 3
        assert len(posURL1) == 3

        # Check if position list is returned in alphabetical order
        assert positionsList1[0] == "Intern: (WLS 1)"
        assert positionsList1[1] == "Lab Assistant: (WLS 2)"
        assert positionsList1[2] == "Teaching Assistant: (WLS 4)"

        # Check if the inactive position is not included in the results
        assert "Research Assistant: (WLS 3)" not in positionsList1

        # Check if posURL contains the correct position codes in the same order as positionsList
        assert posURL1[0] == "S34515"  # Intern
        assert posURL1[1] == "S34514"  # Lab Assistant
        assert posURL1[2] == "S34512"  # Teaching Assistant

        # Check if the inactive position code is not included in posURL
        assert "S34513" not in posURL1  # Research Assistant

        # Check that no positions are returned for a department with no positions
        assert len(positionsList2) == 0
        assert len(posURL2) == 0

        # Check that no positions are returned when department is None
        assert len(positionsList3) == 0
        assert len(posURL3) == 0

        transaction.rollback()

def test_getPositionRevision():
    """
    Test to check if the getPositionRevision function in getPositions.py correctly retrieves a single position for a given department, position code, and optional revision date.
    """
    with mainDB.atomic() as transaction:
        dept = Department.create(departmentID=200, DEPT_NAME="Physics", ACCOUNT="6742", ORG="2116", departmentCompliance=True, isActive=True)

        position1 = PositionHistory.create(positionTitle="Lab Technician",
                                            positionCode="S34516",
                                            department=dept,
                                            status="Inactive",
                                            wls=3,
                                            revisionDate="2024-01-01",
                                            description="")

        position2 = PositionHistory.create(positionTitle="Lab Technician",
                                            positionCode="S34516",
                                            department=dept,
                                            status="Requested",
                                            wls=3,
                                            revisionDate="2025-01-01",
                                            description="")

        position3 = PositionHistory.create(positionTitle="Lab Technician",
                                            positionCode="S34516",
                                            department=dept,
                                            status="Active",
                                            wls=3,
                                            revisionDate="2023-01-01",
                                            description="")

        # Test retrieving the most recent revision - should return regardless of status
        retrieved_position = getPositionRevision(dept, "S34516")
        assert retrieved_position.revisionDate == "2025-01-01"

        # Test retrieving a specific revision - should return regardless of status
        retrieved_position_specific = getPositionRevision(dept, "S34516", "2023-01-01")
        assert retrieved_position_specific.revisionDate == "2023-01-01"
        assert retrieved_position_specific.status == "Active"

        retrieved_position = getPositionRevision(dept, "S34516", "2024-01-01")
        assert retrieved_position.revisionDate == "2024-01-01"
        assert retrieved_position.status == "Inactive"

        retrieved_position_specific = getPositionRevision(dept, "S34516", "2025-01-01")
        assert retrieved_position_specific.revisionDate == "2025-01-01"
        assert retrieved_position_specific.status == "Requested"

        # Test retrieving a non-existent revision date
        retrieved_position_non_existent = getPositionRevision(dept, "S34516", "2099-01-01")
        assert retrieved_position_non_existent is None

        transaction.rollback()
