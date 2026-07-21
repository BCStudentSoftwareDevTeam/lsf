import pytest
from app.models import mainDB
from app.models.department import Department
from app.models.positionHistory import PositionHistory
from app.logic.getPositions import getActivePositions

@pytest.mark.integration
def test_getActivePositions():
    with mainDB.atomic() as transaction:
        dept1 = Department.create(departmentID=1, DEPT_NAME="Computer Science", ACCOUNT="6740", ORG="2114", departmentCompliance=True, isActive=True)

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
                                            revisionDate="2023-01-01",
                                            description="") 

        position4 = PositionHistory.create(positionTitle="Intern",
                                            positionCode="S34515",
                                            department=dept1,
                                            status="Active",
                                            wls=1,
                                            revisionDate="2023-01-01",
                                            description="")

        positionsList, posURL = getActivePositions(dept1)

        # Check that only active positions are returned
        assert len(positionsList) == 3
        assert len(posURL) == 3

        # Check if position list is returned in alphabetical order
        assert positionsList[0] == "Intern: (WLS 1)"
        assert positionsList[1] == "Lab Assistant: (WLS 2)"
        assert positionsList[2] == "Teaching Assistant: (WLS 4)"

        # Check if the inactive position is not included in the results
        assert "Research Assistant: (WLS 3)" not in positionsList

        # Check if posURL contains the correct position codes in the same order as positionsList
        assert posURL[0] == "S34515"  # Intern
        assert posURL[1] == "S34514"  # Lab Assistant
        assert posURL[2] == "S34512"  # Teaching Assistant

        transaction.rollback()

@pytest.mark.integration
def test_checkNoPosition_In_department():
    with mainDB.atomic() as transaction:
        dept2 = Department.create(departmentID=2, DEPT_NAME="Mathematics", ACCOUNT="6741", ORG="2115", departmentCompliance=True, isActive=True)

        positionsList, posURL = getActivePositions(dept2)

        # Check that no positions are returned for a department with no positions
        assert len(positionsList) == 0
        assert len(posURL) == 0

        transaction.rollback()

# what if there the department is None?
def test_checkNoDepartment():
# checks when dept is None (that is similar to when Department.get raises DoesNotExist)
    with mainDB.atomic() as transaction:
        positionsList, posURL = getActivePositions(None)

        # Check that no positions are returned when department is None
        assert len(positionsList) == 0
        assert len(posURL) == 0

        transaction.rollback()
