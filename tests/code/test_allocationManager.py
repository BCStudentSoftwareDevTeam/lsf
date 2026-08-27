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
def testBreakTerm():
    #create
    term = Term.create(termCode = 200601)
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
def testPendingAllocation(testDepartment,testTerm):
    #create
    allocation = Allocation.create(
        termCode       = testTerm.termCode,
        department     = testDepartment.departmentID,
        isFinal        = False,
        approvedOn     = None,
        approvedBy     = None,
        justification  = "pending broski",
        primary_10     = 4,
        primary_12     = 8,
        primary_15     = 7,
        primary_20     = 2,
        secondary_5    = 3,
        secondary_10   = 1,
        breakHours     = 557)

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
    startDate                   = "2006-08-01",
    endDate                     = "2007-5-01",
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
def testBreakLaborStatusForm(testStudent,testSupervisor,testDepartment,testBreakTerm):
    breakLaborStatusForm = LaborStatusForm.create(
    studentName                 = "John Doe",
    laborStatusFormID           = 9898,
    termCode                    = testBreakTerm.termCode,      
    studentSupervisee           = testStudent.ID,
    supervisor_id               = testSupervisor.ID,
    department                  = testDepartment.departmentID,
    jobType                     = "Secondary",
    WLS                         = 1,
    POSN_TITLE                  = "Vacation Worker",
    POSN_CODE                   = "S61412",
    contractHours               = 168,
    weeklyHours                 = None,
    startDate                   = "2006-04-01",
    endDate                     = "2006-09-01",
    supervisorNotes             = None,
    laborDepartmentNotes        = None,
    studentConfirmation         = True,
    confirmationToken           = None,
    studentExpirationDate       = True,
    studentResponseDate         = True,
    )

    breakFormHistory = FormHistory.create(
        formHistoryID = 9898,
        formID_id = "9898",
        historyType_id = "Labor Status Form",
        releaseForm_id = None,
        adjustedForm_id = None,
        overloadForm_id = None,
        createdBy_id = 1,
        createdDate = "2006-02-01",
        reviewedDate = "2006-03-01",
        reviewedBy_id = 1,
        status_id = "Approved",
        rejectReason = None
    )

    yield breakLaborStatusForm, breakFormHistory
      #destroy
    breakLaborStatusForm.delete_instance()

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
def test_getAllocation(testDepartment, testTerm, testAllocation, testPendingAllocation):
    
    allocation = getAllocation(testTerm.termCode, testDepartment)
    assert allocation["justification"] == "broski"
    assert allocation["primary_10"] == 3
    assert allocation["primary_12"] == 7
    assert allocation["primary_15"] == 6
    assert allocation["primary_20"] == 1
    assert allocation["secondary_5"] == 2
    assert allocation["secondary_10"] == 0
    assert allocation["breakHours"] == 556

    allocation = getAllocation(testTerm.termCode, testDepartment, False)
    assert allocation["justification"] == "pending broski"
    assert allocation["primary_10"] == 4
    assert allocation["primary_12"] == 8
    assert allocation["primary_15"] == 7
    assert allocation["primary_20"] == 2
    assert allocation["secondary_5"] == 3
    assert allocation["secondary_10"] == 1
    assert allocation["breakHours"] == 557

@pytest.mark.integration
def test_getTotalAllocations(testDepartment, testTerm, testAllocation):
    totalAllocation = getTotalAllocations(testTerm.termCode,testDepartment)
    assert totalAllocation['totalPrimaries'] == 17
    assert totalAllocation['totalSecondaries'] == 2
    assert totalAllocation['totalAllocations'] == 19

@pytest.mark.integration
def test_countContracts(testLaborStatusForm, testTerm, testDepartment, testFormHistory):
    contractsCounts = countContracts(testLaborStatusForm.jobType, testLaborStatusForm.weeklyHours, testTerm.termCode, testDepartment.departmentID)
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

    assert contractedAllocation['used_primaries'] == 1
    assert contractedAllocation['used_secondaries'] == 0
    assert contractedAllocation['used_total'] == 1

    assert contractedAllocation['break_hours'] == 500

@pytest.mark.integration
<<<<<<< HEAD:tests/code/test_allocationManger.py
def test_getContractedAllocations_withoutAnAllocationRow(testLaborStatusForm, testTerm, testDepartment, testFormHistory):
    '''
    getContractedAllocations must not require an Allocation row to exist for
    the department/term (e.g. before one has been created or finalized) -
    it should still report the LaborStatusForm-derived counts.
    '''
    contractedAllocation = getContractedAllocations(testTerm.termCode, testDepartment.departmentID)
    assert contractedAllocation['used_15'] == 1
    assert contractedAllocation['break_hours'] == 500

@pytest.mark.integration
def test_getContractedAllocations_sumsBreakHoursAcrossAcademicYearCode(testDepartment, testStudent, testSupervisor, testUser):
    '''
    A department can have approved break-term contracts under both a specific
    term and that year's academic-year "00" bucket term - break_hours should
    sum both, not silently keep only whichever one the query happens to see
    first.
    '''
    specificTerm = Term.create(termCode=200610)
    academicYearTerm = Term.create(termCode=200600)  # matches testTerm's code

    specificTermForm = LaborStatusForm.create(
        laborStatusFormID=9001, termCode=specificTerm, studentSupervisee=testStudent,
        supervisor_id=testSupervisor.ID, department=testDepartment, jobType="Primary", WLS=1,
        POSN_TITLE="Specific Term Break", POSN_CODE="S9001", contractHours=100, weeklyHours=None,
    )
    FormHistory.create(
        formHistoryID=9001, formID=specificTermForm, historyType="Labor Status Form",
        createdBy=testUser.userID, createdDate="2025-03-02", status="Approved",
    )

    academicYearForm = LaborStatusForm.create(
        laborStatusFormID=9002, termCode=academicYearTerm, studentSupervisee=testStudent,
        supervisor_id=testSupervisor.ID, department=testDepartment, jobType="Primary", WLS=1,
        POSN_TITLE="Academic Year Break", POSN_CODE="S9002", contractHours=250, weeklyHours=None,
    )
    FormHistory.create(
        formHistoryID=9002, formID=academicYearForm, historyType="Labor Status Form",
        createdBy=testUser.userID, createdDate="2025-03-02", status="Approved",
    )

    try:
        contractedAllocation = getContractedAllocations(specificTerm.termCode, testDepartment.departmentID)
        assert contractedAllocation['break_hours'] == 350  # 100 + 250, both terms summed
    finally:
        specificTermForm.delete_instance()
        academicYearForm.delete_instance()
        specificTerm.delete_instance()
        academicYearTerm.delete_instance()
=======
def test_getBreakContracts(testBreakLaborStatusForm, testBreakTerm, testDepartment,testTerm):

    # Test that the formHistory object exists
    breakContractHours = getBreakContracts(testBreakTerm, testDepartment)
    assert breakContractHours == 168
    
    # Test it with a higher amount of hours
    testBreakLaborStatusForm[0].contractHours  = 800
    testBreakLaborStatusForm[0].save()

    breakContractHours = getBreakContracts(testBreakTerm, testDepartment)
    assert breakContractHours == 800

    # Test that it works even if weeklyHours and contractHours are set
    testBreakLaborStatusForm[0].weeklyHours  = 9999
    testBreakLaborStatusForm[0].save()

    breakContractHours = getBreakContracts(testBreakTerm, testDepartment)
    assert breakContractHours == 800

    # Test that if the form is denied to not show up.
    testBreakLaborStatusForm[1].status  = "denied by student"
    testBreakLaborStatusForm[1].save()

    breakContractHours = getBreakContracts(testBreakTerm, testDepartment)
    assert breakContractHours == 0

    # Test if the term changes to a non-break term
    testBreakLaborStatusForm[0].termCode = testTerm
    testBreakLaborStatusForm[0].save()
    testBreakLaborStatusForm[1].status  = "Approved"
    testBreakLaborStatusForm[1].save()
    
    breakContractHours = getBreakContracts(testBreakTerm, testDepartment)
    assert breakContractHours == 0
    
>>>>>>> f0ab8139ac7ae3967301c5e539fd15f4e69896ec:tests/code/test_allocationManager.py
