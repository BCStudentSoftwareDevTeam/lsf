import pytest
from app.models import mainDB
from app.models.department import Department
from app.models.positionHistory import PositionHistory
from app.logic.getPositions import getActivePositions

@pytest.mark.integration
def test_getActivePositions():
    """
    Test to check if the getActivePositions function in getPositions.py correctly retrieves active positions for a single department.
    """
    with mainDB.atomic() as transaction:
        dept1 = Department.create(departmentID=100, DEPT_NAME="Computer Science", ACCOUNT="6740", ORG="2114", departmentCompliance=True, isActive=True)

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
def test_checkNoPositionInDepartment(): 
    """
    Checks the behavior of getActivePositions when there are no positions in the department.
    It should return empty lists for both positionsList and posURL, indicating that no positions are available for the department.
    """
    with mainDB.atomic() as transaction:
        dept5 = Department.create(departmentID=101, DEPT_NAME="Mathematics", ACCOUNT="6741", ORG="2115", departmentCompliance=True, isActive=True)

        positionsList, posURL = getActivePositions(dept5)

        # Check that no positions are returned for a department with no positions
        assert len(positionsList) == 0
        assert len(posURL) == 0

        transaction.rollback()

# what if there the department is None?
@pytest.mark.integration
def test_checkNoDepartment():
    """
    Checks the behavior of getActivePositions when the department is None. 
    It should return empty lists for both positionsList and posURL, indicating that no positions are available for a non-existent department.
    """
# checks when dept is None (that is similar to when Department.get raises DoesNotExist)
    with mainDB.atomic() as transaction:
        positionsList, posURL = getActivePositions(None)

        # Check that no positions are returned when department is None
        assert len(positionsList) == 0
        assert len(posURL) == 0

        transaction.rollback()

@pytest.mark.integration
def test_checkPositionDuplicates():
    """
    Test to check if the function correctly handles duplicate position codes within the same department and duplicate elements across different departments.
    """
    with mainDB.atomic() as transaction:
        deptA = Department.create(departmentID=102, DEPT_NAME="Computer Science", ACCOUNT="6740", ORG="2114", departmentCompliance=True, isActive=True)
        deptB = Department.create(departmentID=103, DEPT_NAME="Mathematics", ACCOUNT="6741", ORG="2115", departmentCompliance=True, isActive=True)
        deptC = Department.create(departmentID=104, DEPT_NAME="Physics", ACCOUNT="6742", ORG="2116", departmentCompliance=True, isActive=True)
        deptD = Department.create(departmentID=105, DEPT_NAME="Chemistry", ACCOUNT="6743", ORG="2117", departmentCompliance=True, isActive=True)
        
        position5 = PositionHistory.create(positionTitle="Teaching Assistant", 
                                            positionCode="S34522", 
                                            department=deptA, 
                                            status="Active", 
                                            wls=4,
                                            revisionDate="2023-01-01", 
                                            description="")
        
        position5Dup = PositionHistory.create(positionTitle="Teaching Assistant", # Duplicate position from the same department, but with a different status (Inactive).
                                            positionCode="S34522", 
                                            department=deptA, 
                                            status="Inactive", 
                                            wls=4,
                                            revisionDate="2023-01-01", 
                                            description="")

        position9 = PositionHistory.create(positionTitle="Teaching Assistant",
                                            positionCode="S34526", 
                                            department=deptA, 
                                            status="Active", 
                                            wls=4,
                                            revisionDate="2023-01-01", 
                                            description="")
        
        # Note: position5DepartmentBCopy intentionally uses a different revisionDate
        # (2026-01-01) than position5 (2023-01-01) to confirm revisionDate does NOT
        # factor into which department keeps a contested positionCode.
        position5DepartmentBCopy = PositionHistory.create(positionTitle="Book Handler", 
                                            positionCode="S34522", 
                                            department=deptB, 
                                            status="Active", 
                                            wls=4,
                                            revisionDate="2026-01-01", 
                                            description="")
        
        position6 = PositionHistory.create(positionTitle="Research Assistant",
                                            positionCode="S34523",
                                            department=deptB,
                                            status="Active",
                                            wls=3,
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
                                            status="Inactive",
                                            wls=1,
                                            revisionDate="2023-01-01",
                                            description="")
        
        # Get the active positions for each department
        positionsListA, posURLA = getActivePositions(deptA) 
        positionsListB, posURLB = getActivePositions(deptB)
        positionsListC, posURLC = getActivePositions(deptC)
        positionsListD, posURLD = getActivePositions(deptD)

        # Check that the correct number of active positions are returned for each department
        assert len(positionsListA) == 2 # Has a duplicate position name, should return 2 unique active positions due to unique position codes. 
        assert len(posURLA) == 2
        
        # Check if two different departments with the same position code are counted as separate active positions for each department.
        # The position with code "S34522" is active in department A, so it should not be counted as active in department B.
        assert len(positionsListB) == 1
        assert len(posURLB) == 1

        assert len(positionsListC) == 1
        assert len(posURLC) == 1

        assert len(positionsListD) == 0
        assert len(posURLD) == 0

        # Check that the correct position titles and codes are returned for department B and A (Focused on the contested position code "S34522" due to the duplicate across departments) 
        assert "Research Assistant: (WLS 3)" in positionsListB
        assert "Book Handler: (WLS 4)" not in positionsListB
        assert "Book Handler: (WLS 4)" not in positionsListA
        assert "S34523" in posURLB
        assert "S34522" not in posURLB
        transaction.rollback()

@pytest.mark.integration
def test_checkPositionClaimOrderIndependentOfDeptOrder():
    """
    Checks that the order of department creation does not affect which department receives a contested position code.
    The department that created the position first (based on the auto-incrementing ID) should be the one that retains the active position, regardless of the order in which departments were created.
    """
    with mainDB.atomic() as transaction:
        deptA = Department.create(departmentID=106, 
                                  DEPT_NAME="Biology", 
                                  ACCOUNT="6744", 
                                  ORG="2118", 
                                  departmentCompliance=True, 
                                  isActive=True)
        
        deptB = Department.create(departmentID=107, 
                                  DEPT_NAME="History", 
                                  ACCOUNT="6745", 
                                  ORG="2119", 
                                  departmentCompliance=True, 
                                  isActive=True)

        # deptB's row is created FIRST
        positionB = PositionHistory.create(positionTitle="Archivist", 
                                           positionCode="S99001", 
                                           department=deptB, 
                                           status="Active", wls=2, 
                                           revisionDate="2023-01-01", 
                                           description="")
        
        positionA = PositionHistory.create(positionTitle="Curator", 
                                           positionCode="S99001", 
                                           department=deptA, 
                                           status="Active", 
                                           wls=2, 
                                           revisionDate="2023-01-01", 
                                           description="")

        positionsListA, posURLA = getActivePositions(deptA)
        positionsListB, posURLB = getActivePositions(deptB)

        # deptB claimed the code first therefore deptA should lose it, not deptB
        assert len(positionsListA) == 0
        assert len(positionsListB) == 1
        assert "Archivist: (WLS 2)" in positionsListB

        transaction.rollback()

@pytest.mark.integration
def test_checkDuplicateActiveWithinSameDepartment():
    """
    Checks that if the same department has two active positions with the same position code, only one of them is counted in the results.
    This test ensures that the function correctly filters out duplicates based on position code within the same department
    """
    with mainDB.atomic() as transaction:
        dept = Department.create(departmentID=108, 
                                 DEPT_NAME="Art", 
                                 ACCOUNT="6746", 
                                 ORG="2120", 
                                 departmentCompliance=True, 
                                 isActive=True)

        # Create two active positions with the same code in the same department
        pos1 = PositionHistory.create(positionTitle="Assistant A", 
                                      positionCode="S99002", 
                                      department=dept, 
                                      status="Active", 
                                      wls=1, 
                                      revisionDate="2023-01-01", 
                                      description="")
        
        pos2 = PositionHistory.create(positionTitle="Assistant B", 
                                      positionCode="S99002", 
                                      department=dept, 
                                      status="Active", 
                                      wls=1, 
                                      revisionDate="2023-06-01", 
                                      description="")

        positionsList, posURL = getActivePositions(dept)

        # Only one should be counted despite two Active rows with the same code
        assert len(positionsList) == 1
        assert len(posURL) == 1

        transaction.rollback()

@pytest.mark.integration
def test_checkThreeWayPositionCodeConflict():
    """
    Checks that if three different departments have active positions with the same position code, 
    only the department that created the position first (based on the auto-incrementing ID) retains the active position.
    """
    with mainDB.atomic() as transaction:
        deptA = Department.create(departmentID=109, 
                                  DEPT_NAME="Physics2", 
                                  ACCOUNT="6747", 
                                  ORG="2121", 
                                  departmentCompliance=True, 
                                  isActive=True)
        
        deptB = Department.create(departmentID=110, 
                                  DEPT_NAME="Chem2", 
                                  ACCOUNT="6748", 
                                  ORG="2122", 
                                  departmentCompliance=True, 
                                  isActive=True)
        
        deptC = Department.create(departmentID=111, 
                                  DEPT_NAME="Bio2", 
                                  ACCOUNT="6749", 
                                  ORG="2123", 
                                  departmentCompliance=True, 
                                  isActive=True)

        # Create three active positions with the same code in different departments
        posA = PositionHistory.create(positionTitle="First Claim", 
                                      positionCode="S99003", 
                                      department=deptA, 
                                      status="Active", 
                                      wls=1, 
                                      revisionDate="2023-01-01", 
                                      description="")
        
        posB = PositionHistory.create(positionTitle="Second Claim", 
                                      positionCode="S99003", 
                                      department=deptB, 
                                      status="Active", 
                                      wls=1, 
                                      revisionDate="2023-01-01", 
                                      description="")
        
        posC = PositionHistory.create(positionTitle="Third Claim", 
                                      positionCode="S99003", 
                                      department=deptC, 
                                      status="Active", 
                                      wls=1, 
                                      revisionDate="2023-01-01", 
                                      description="")

        listA, urlA = getActivePositions(deptA)
        listB, urlB = getActivePositions(deptB)
        listC, urlC = getActivePositions(deptC)

        assert len(listA) == 1  # only the first-created claim survives
        assert len(listB) == 0
        assert len(listC) == 0

        transaction.rollback()

@pytest.mark.integration
def test_checkInactiveElsewhereDoesNotBlockActiveClaim():
    """
    Checks that if a department has an inactive position with a certain position code, it does not block another department from claiming that position code as active.
    """
    with mainDB.atomic() as transaction:
        deptA = Department.create(departmentID=114, DEPT_NAME="Geology", ACCOUNT="6752", ORG="2126", departmentCompliance=True, isActive=True)
        deptB = Department.create(departmentID=115, DEPT_NAME="Astronomy", ACCOUNT="6753", ORG="2127", departmentCompliance=True, isActive=True)

        # Create an inactive position in deptA and an active position in deptB with the same code
        PositionHistory.create(positionTitle="Old Role", 
                               positionCode="S99005", 
                               department=deptA, 
                               status="Inactive", 
                               wls=1, 
                               revisionDate="2020-01-01", 
                               description="")
        
        PositionHistory.create(positionTitle="Current Role", 
                               positionCode="S99005", 
                               department=deptB, 
                               status="Active", 
                               wls=1, 
                               revisionDate="2023-01-01", 
                               description="")

        listB, urlB = getActivePositions(deptB)

        # deptA's row is Inactive, so it should never block deptB's Active claim
        assert len(listB) == 1
        assert "Current Role: (WLS 1)" in listB

        transaction.rollback()