import pytest

from app.models import mainDB
from app.models.allocation import Allocation
from app.models.laborStatusForm import * 
from app.models.department import *
from app.models.term import *
from app.models.formHistory import FormHistory

from app.logic.allocationManager import *

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

    #destroy
    department.delete_instance()

@pytest.fixture
def testTerm():
    #create
    term = Term.create(termCode = 200600)
    yield term

    #destroy
    term.delete_instance()

@pytest.fixture
def testAllocation():
    #create
    allocation = Allocation.create(
        termCode       = 200600,
        department     = 9999,
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


@pytest.mark.integration
def test_getAllocation(testDepartment, testTerm, testAllocation):
    print(f"\n\ntestDepartment: {testDepartment.__dict__}\n",
          f"\n\ntestTerm:       {testTerm.__dict__}\n",
          f"\n\ntestAllocation: {testAllocation.__dict__}\n",)
