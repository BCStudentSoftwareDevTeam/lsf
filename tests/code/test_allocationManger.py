import pytest

from app.models import mainDB
from app.models.allocation import Allocation
from app.models.laborStatusForm import * 
from app.models.department import *
from app.models.term import *
from app.models.formHistory import FormHistory
from app.models.student import *
from app.models.supervisor import * 
from app.models.historyType import * 
from app.models.user import User

from app.logic.allocationManager import *


@pytest.fixture
def testUser():
    user = User.create(
        userID = "B12323435",
        username="test"
    )
    yield user
    user.delete_instance()

@pytest.fixture
def testDepartment():
    #create
    department = Department.create(
        departmentID            = 9999,
        DEPT_NAME               = "Testing Department of Tests",
        ACCOUNT                 = 6740,
        ORG                     = 9284,
        departmentCompliance    = True,
        isActive                = True)

    yield department

    #destroyLabor Status
    department.delete_instance()

@pytest.fixture
def testTerm():
    #create
    term = Term.create(termCode = 200600)
    yield term

    #destroy
    term.delete_instance()

@pytest.fixture
def testAllocation(testDepartment,testTerm):
    #create
    allocation = Allocation.create(
        termCode       = testTerm.termCode,
        department     = testDepartment.departmentID,
        isFinal        = True,
        approvedOn     = None,
        approvedBy     = None,
        justification  = "broski",
        primary_10     = 3,
        primary_12     = 7,
        primary_15     = 6,
        primary_20     = 1,
        secondary_5    = 2,
        secondary_10   = 0,
        breakHours     = 556)

    yield allocation

    #destroy
    allocation.delete_instance()

@pytest.fixture
def testStudent():
    student_data = Student.create(
    ID              = "B12323435"		        # B-number
    )
    yield student_data

    #destroy
    student_data.delete_instance()

@pytest.fixture
def testSupervisor():
    supervisor_data = Supervisor.create(
    ID              = "B12323435"		        # B-number
    )
    yield supervisor_data
    #destroy
    supervisor_data.delete_instance()

@pytest.fixture
def testHistoryType():
    History_data = HistoryType.create(
        historyTypeName = "Labor Status Form"
    )
    yield History_data
    #destroy
    History_data.delete_instance()

@pytest.fixture
def testLaborStatusForm(testStudent,testSupervisor,testDepartment,testTerm):
    laborStatusForm = LaborStatusForm.create(
    studentName                 = "John Doe",
    laborStatusFormID           = 8989,
    termCode                    = testTerm.termCode,      
    studentSupervisee           = testStudent.ID,
    supervisor_id               = testSupervisor.ID,
    department                  = testDepartment.departmentID,
    jobType                     = "Primary",
    WLS                         = 1,
    POSN_TITLE                  = "Break Worker",
    POSN_CODE                   = "S61412",
    contractHours               = 500,
    weeklyHours                 = 15,
    startDate                   = "2025-04-01",
    endDate                     = "2025-09-01",
    supervisorNotes             = None,
    laborDepartmentNotes        = None,
    studentConfirmation         = True,
    confirmationToken           = None,
    studentExpirationDate       = True,
    studentResponseDate         = True,
    )

    yield laborStatusForm
      #destroy
    laborStatusForm.delete_instance()

@pytest.fixture
def testFormHistory(testLaborStatusForm,testUser):
    formHistory = FormHistory.create(
        formHistoryID = 8989,
        formID        = testLaborStatusForm,      # pass the model instance
        historyType   = "Labor Status Form", 
        createdBy     = testUser.userID,
        createdDate   = "2025-03-02",
        status        = "Approved",
    )
    yield formHistory
    formHistory.delete_instance()

@pytest.mark.integration
def test_getAllocation(testDepartment, testTerm, testAllocation):
    
    allocation = getAllocation(testTerm.termCode, testDepartment)
    assert allocation["primary_10"] == 3
    assert allocation["primary_12"] == 7
    assert allocation["primary_15"] == 6
    assert allocation["primary_20"] == 1
    assert allocation["secondary_5"] == 2
    assert allocation["secondary_10"] == 0
    assert allocation["breakHours"] == 556

@pytest.mark.integration
def test_getTotalAllocations(testDepartment, testTerm, testAllocation):
    totalAllocation = getTotalAllocations(testTerm.termCode,testDepartment)
    assert totalAllocation['totalPrimaries'] == 17
    assert totalAllocation['totalSecondaries'] == 2
    assert totalAllocation['totalAllocations'] == 19

@pytest.mark.integration
def test_countContracts(testLaborStatusForm, testTerm, testDepartment, testFormHistory):
    contractsCounts = countContracts(testLaborStatusForm.jobType,testLaborStatusForm.weeklyHours,testTerm.termCode,testDepartment.departmentID)
    assert contractsCounts == 1

@pytest.mark.integration
def test_getContractedAllocations(testLaborStatusForm, testTerm, testDepartment, testFormHistory,testAllocation):
    contractedAllocation = getContractedAllocations(testTerm.termCode,testDepartment.departmentID)
    assert contractedAllocation['used_10'] == 0
    assert contractedAllocation['used_12'] == 0
    assert contractedAllocation['used_15'] == 1
    assert contractedAllocation['used_20'] == 0
    assert contractedAllocation['used_5_sec'] == 0
    assert contractedAllocation['used_10_sec'] == 0
    assert contractedAllocation['used_total'] == 1
    assert contractedAllocation['break_hours'] == 500