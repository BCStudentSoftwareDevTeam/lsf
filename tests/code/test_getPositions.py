import pytest
from app.models import mainDB
from app.models.department import Department
from app.models.positionHistory import PositionHistory
from app.logic.getPositions import getActivePositions

@pytest.mark.integration
def test_getActivePositions(): # Test results in duplicate errors.
    """
    
    """
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

        # Check if the inactive position code is not included in posURL
        assert "S34513" not in posURL  # Research Assistant

        transaction.rollback()

@pytest.mark.integration
def test_checkNoPositionInDepartment(): # Test results in duplicate errors.
    """
    
    """
    with mainDB.atomic() as transaction:
        dept5 = Department.create(departmentID=2, DEPT_NAME="Mathematics", ACCOUNT="6741", ORG="2115", departmentCompliance=True, isActive=True)

        positionsList, posURL = getActivePositions(dept5)

        # Check that no positions are returned for a department with no positions
        assert len(positionsList) == 0
        assert len(posURL) == 0

        transaction.rollback()

# what if there the department is None?
@pytest.mark.integration
def test_checkNoDepartment(): # Test passes.
    """
    
    """
# checks when dept is None (that is similar to when Department.get raises DoesNotExist)
    with mainDB.atomic() as transaction:
        positionsList, posURL = getActivePositions(None)

        # Check that no positions are returned when department is None
        assert len(positionsList) == 0
        assert len(posURL) == 0

        transaction.rollback()

@pytest.mark.integration
def test_checkPositionAcrossDepartments(): # Test results in duplicate errors.
    with mainDB.atomic() as transaction:
        deptA = Department.create(departmentID=1, DEPT_NAME="Computer Science", ACCOUNT="6740", ORG="2114", departmentCompliance=True, isActive=True)
        deptB = Department.create(departmentID=2, DEPT_NAME="Mathematics", ACCOUNT="6741", ORG="2115", departmentCompliance=True, isActive=True)
        deptC = Department.create(departmentID=3, DEPT_NAME="Physics", ACCOUNT="6742", ORG="2116", departmentCompliance=True, isActive=True)
        deptD = Department.create(departmentID=4, DEPT_NAME="Chemistry", ACCOUNT="6743", ORG="2117", departmentCompliance=True, isActive=True)
        
        position5 = PositionHistory.create(positionTitle="Teaching Assistant", 
                                            positionCode="S34522", 
                                            department=deptA, 
                                            status="Active", 
                                            wls=4,
                                            revisionDate="2023-01-01", 
                                            description="")
        
        position5Dup = PositionHistory.create(positionTitle="Teaching Assistant", # Duplicate active position in the same department (Unsure if this should count as 1 or 2 active positions (Double Check with the team))
                                            positionCode="S34522", 
                                            department=deptA, 
                                            status="Active", 
                                            wls=4,
                                            revisionDate="2023-01-01", 
                                            description="")
        
        position6 = PositionHistory.create(positionTitle="Research Assistant",
                                            positionCode="S34523",
                                            department=deptB,
                                            status="Active",
                                            wls=3,
                                            revisionDate="2023-01-01",
                                            description="")
        
        position5DepartmentBCopy = PositionHistory.create(positionTitle="Teaching Assistant", 
                                            positionCode="S34522", 
                                            department=deptB, 
                                            status="Active", 
                                            wls=4,
                                            revisionDate="2023-01-01", 
                                            description="")
        
        position7 = PositionHistory.create(positionTitle="Lab Assistant",
                                            positionCode="S34524",
                                            department=deptC,
                                            status="Active",
                                            wls=2,
                                            revisionDate="2023-01-01",
                                            description="") 

        position8 = PositionHistory.create(positionTitle="Intern",
                                            positionCode="S34525",
                                            department=deptD,
                                            status="Active",
                                            wls=1,
                                            revisionDate="2023-01-01",
                                            description="")
        
        positionsListA, posURLA = getActivePositions(deptA) 
        positionsListB, posURLB = getActivePositions(deptB)
        positionsListC, posURLC = getActivePositions(deptC)
        positionsListD, posURLD = getActivePositions(deptD)

        # Check that the correct number of active positions are returned for each department
        assert len(positionsListA) == 2 # Has a duplicate active position, should return 2 unique active positions 
        assert len(posURLA) == 2
        
        # Check if two different departments with the same position title and code are counted as separate active positions for each department.
        assert len(positionsListB) == 2 # Has a duplicate active position with another department, should still return 2 unique active positions (Organized by Department)
        assert len(posURLB) == 2

        assert len(positionsListC) == 1
        assert len(posURLC) == 1

        assert len(positionsListD) == 1
        assert len(posURLD) == 1
        

        transaction.rollback()