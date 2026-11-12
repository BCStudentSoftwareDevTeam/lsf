import pytest
from app.models import mainDB
from app.models.term import Term
from app.models.department import Department
from app.models.allocation import Allocation
from app.models.laborStatusForm import LaborStatusForm
from app.models.formHistory import FormHistory
from app.models.student import Student
from app.models.supervisor import Supervisor
from app.models.user import User
from app.logic.allocationManager import getAllocationSummary, getOverAllocatedBands, getAllocationWarning


@pytest.fixture
def allocationData():
    '''
    An empty department with an academic-year term and one of its break terms, rolled back after each test.
    '''
    with mainDB.atomic() as transaction:
        data = {
            'dept': Department.create(departmentID=9997, DEPT_NAME="Allocation Test Department",
                                      ACCOUNT=6741, ORG=9285, departmentCompliance=True, isActive=True),
            'term': Term.create(termCode=200800),
            'breakTerm': Term.create(termCode=200801, isBreak=True),
            'student': Student.create(ID="B99999001"),
            'supervisor': Supervisor.create(ID="B99999002"),
            'user': User.create(username="allocationTester"),
        }
        yield data
        transaction.rollback()


def createAllocation(data, primary_10=0, primary_12=0, primary_15=0, primary_20=0,
                     secondary_5=0, secondary_10=0, breakHours=0, isFinal=True):
    return Allocation.create(termCode=data['term'], department=data['dept'], isFinal=isFinal, justification="test",
                             primary_10=primary_10, primary_12=primary_12, primary_15=primary_15, primary_20=primary_20,
                             secondary_5=secondary_5, secondary_10=secondary_10, breakHours=breakHours)


def createContract(data, jobType="Primary", weeklyHours=None, contractHours=None, term=None, status="Approved"):
    # Year-long dates, so countContracts counts the form toward the academic-year term.
    lsf = LaborStatusForm.create(termCode=term or data['term'], studentSupervisee=data['student'],
                                 supervisor=data['supervisor'], department=data['dept'], jobType=jobType, WLS=1,
                                 POSN_TITLE="Test Position", POSN_CODE="S00000", weeklyHours=weeklyHours,
                                 contractHours=contractHours, startDate="2008-08-01", endDate="2009-05-01")
    FormHistory.create(formID=lsf, historyType="Labor Status Form", createdBy=data['user'],
                       createdDate="2008-07-01", status=status)
    return lsf


@pytest.mark.integration
def test_getAllocationSummary_usesAllocationManagerCounts(allocationData):
    createAllocation(allocationData, primary_10=2, primary_15=1, secondary_5=1, breakHours=100)
    createContract(allocationData, weeklyHours=10)
    createContract(allocationData, weeklyHours=10, status="Pending")
    createContract(allocationData, weeklyHours=15, status="Denied by Admin")  # denied forms don't count
    createContract(allocationData, jobType="Secondary", contractHours=40, term=allocationData['breakTerm'])

    summary = getAllocationSummary(allocationData['term'].termCode, allocationData['dept'])

    assert summary['allocation']['primary_10'] == 2
    assert summary['allocationBands']['primary_10'] == {'used': 2, 'allocated': 2}
    assert summary['allocationBands']['primary_15'] == {'used': 0, 'allocated': 1}
    assert summary['totalPositionsAllocated'] == 4
    assert summary['totalPositionsUsed'] == 2
    assert summary['breakHoursUsed'] == 40


@pytest.mark.integration
def test_getAllocationSummary_ignoresDraftAllocations(allocationData):
    createAllocation(allocationData, primary_10=5, isFinal=False)

    summary = getAllocationSummary(allocationData['term'].termCode, allocationData['dept'])

    assert summary['allocation'] is None


@pytest.mark.integration
def test_getAllocationWarning_returnsNoneWithoutAnAllocationRow(allocationData):
    assert getAllocationWarning(allocationData['term'].termCode, allocationData['dept']) is None


@pytest.mark.integration
def test_getAllocationWarning_fallsBackToTheAcademicYearAllocation(allocationData):
    createAllocation(allocationData, primary_10=3)
    Term.create(termCode=200811)  # Fall

    warning = getAllocationWarning(200811, allocationData['dept'])

    assert warning['totalPositionsAllocated'] == 3


@pytest.mark.integration
def test_getAllocationWarning_underAllocated(allocationData):
    createAllocation(allocationData, primary_10=5, primary_12=5, primary_15=5, primary_20=5,
                     secondary_5=5, secondary_10=5, breakHours=100)
    createContract(allocationData, weeklyHours=10)

    warning = getAllocationWarning(allocationData['term'].termCode, allocationData['dept'])

    assert warning['totalPositionsUsed'] == 1
    assert warning['positionsRemaining'] == 29
    assert warning['overAllocatedBands'] == []
    assert warning['isPositionsOverAllocated'] is False
    assert warning['isBreakHoursOverAllocated'] is False
    assert warning['isOverAllocated'] is False


@pytest.mark.integration
def test_getAllocationWarning_lowerHourPrimaryCanUseHigherHourSlots(allocationData):
    ''' A 10 hour Primary with no 10 hour slots left can fill an unused 12 hour slot. '''
    createAllocation(allocationData, primary_10=0, primary_12=1, breakHours=100)
    createContract(allocationData, weeklyHours=10)

    warning = getAllocationWarning(allocationData['term'].termCode, allocationData['dept'])

    assert warning['overAllocatedBands'] == []
    assert warning['isOverAllocated'] is False


@pytest.mark.integration
def test_getAllocationWarning_higherHourPrimaryCannotUseLowerHourSlots(allocationData):
    ''' A department within its total positions is still over when a 20 hour Primary has no 20 hour slot. '''
    createAllocation(allocationData, primary_10=5, primary_20=0, breakHours=100)
    createContract(allocationData, weeklyHours=20)

    warning = getAllocationWarning(allocationData['term'].termCode, allocationData['dept'])

    assert warning['positionsRemaining'] == 4
    assert warning['overAllocatedBands'] == [{'label': "20+ Hour Primary", 'used': 1, 'allocated': 0}]
    assert warning['isPositionsOverAllocated'] is True
    assert warning['isPositionsTotalOverAllocated'] is False
    assert warning['isOverAllocated'] is True


@pytest.mark.integration
def test_getAllocationWarning_overOnAggregatePositions(allocationData):
    createAllocation(allocationData, breakHours=100)
    createContract(allocationData, weeklyHours=10)

    warning = getAllocationWarning(allocationData['term'].termCode, allocationData['dept'])

    assert warning['positionsRemaining'] == -1
    assert warning['isPositionsTotalOverAllocated'] is True
    assert warning['isOverAllocated'] is True


@pytest.mark.integration
def test_getAllocationWarning_overOnBreakHours(allocationData):
    createAllocation(allocationData, primary_10=1, breakHours=550)
    createContract(allocationData, jobType="Secondary", contractHours=600, term=allocationData['breakTerm'])

    warning = getAllocationWarning(allocationData['term'].termCode, allocationData['dept'])

    assert warning['breakHoursAllocated'] == 550
    assert warning['breakHoursUsed'] == 600
    assert warning['breakHoursRemaining'] == -50
    assert warning['isBreakHoursOverAllocated'] is True
    assert warning['isOverAllocated'] is True


def bands(primary_10=(0, 0), primary_12=(0, 0), primary_15=(0, 0), primary_20=(0, 0),
          secondary_5=(0, 0), secondary_10=(0, 0)):
    ''' Builds allocationBands from (used, allocated) pairs. '''
    pairs = {'primary_10': primary_10, 'primary_12': primary_12, 'primary_15': primary_15,
             'primary_20': primary_20, 'secondary_5': secondary_5, 'secondary_10': secondary_10}
    return {fieldName: {'used': used, 'allocated': allocated} for fieldName, (used, allocated) in pairs.items()}


def test_getOverAllocatedBands_tenHourContractsFillHigherSlots():
    # 10 slots in each band gives 10 hour contracts 40 accessible slots (10 + 30 from the higher bands).
    assert getOverAllocatedBands(bands(primary_10=(40, 10), primary_12=(0, 10),
                                       primary_15=(0, 10), primary_20=(0, 10))) == []
    assert getOverAllocatedBands(bands(primary_10=(41, 10), primary_12=(0, 10),
                                       primary_15=(0, 10), primary_20=(0, 10))) == [
        {'label': "10+ Hour Primary", 'used': 41, 'allocated': 40}]


def test_getOverAllocatedBands_higherSlotsTakenByTheirOwnBand():
    # The 15 hour contracts use up the 15 and 20 hour slots, leaving the 10 hour contracts only 10 + 10.
    assert getOverAllocatedBands(bands(primary_10=(21, 10), primary_12=(0, 10),
                                       primary_15=(20, 10), primary_20=(0, 10))) == [
        {'label': "10+ Hour Primary", 'used': 41, 'allocated': 40}]


def test_getOverAllocatedBands_fiveHourSecondaryFillsTenHourSecondarySlots():
    assert getOverAllocatedBands(bands(secondary_5=(2, 1), secondary_10=(0, 5))) == []
    # A 10 hour Secondary can't use a 5 hour slot, so being over at 10 hours is also over overall.
    assert getOverAllocatedBands(bands(secondary_5=(0, 1), secondary_10=(2, 1))) == [
        {'label': "10+ Hour Secondary", 'used': 2, 'allocated': 1}]


def test_getOverAllocatedBands_reportsEachShortageOnce():
    # One missing 20 hour slot shouldn't also be reported as 15+, 12+ and 10+...
    assert getOverAllocatedBands(bands(primary_10=(1, 1), primary_15=(1, 1), primary_20=(1, 0))) == [
        {'label': "20+ Hour Primary", 'used': 1, 'allocated': 0}]
    # ...but a further shortage lower down is.
    assert getOverAllocatedBands(bands(primary_10=(2, 1), primary_20=(1, 0))) == [
        {'label': "10+ Hour Primary", 'used': 3, 'allocated': 1},
        {'label': "20+ Hour Primary", 'used': 1, 'allocated': 0}]


def test_getOverAllocatedBands_primaryAndSecondaryDoNotShareSlots():
    # Spare Primary slots can't cover an extra Secondary, or the other way around.
    assert getOverAllocatedBands(bands(primary_20=(0, 5), secondary_10=(1, 0))) == [
        {'label': "10+ Hour Secondary", 'used': 1, 'allocated': 0}]
    assert getOverAllocatedBands(bands(primary_10=(1, 0), secondary_10=(0, 5))) == [
        {'label': "10+ Hour Primary", 'used': 1, 'allocated': 0}]
