from flask import g, abort
from peewee import fn

from app.controllers.main_routes import departmentPortal
from app.controllers.admin_routes.termManagement import createTerms

from app.models.laborStatusForm import *
from app.models.formHistory import *
from app.models.allocation import *
from app.models.department import *
from app.models.term import *

from app.login_manager import require_login



def getUsedBreakHours(term):
    """
    Returns the total number of break hours used by each department for a given term.
    """
    
    # THE PREVIOUS IMPLEMENTATION OF THIS FUNCTION (CAN BE USED IN CASE THE CURRENT IMPLEMENTATION DOESN'T WORK PROPERLY)
    # totalBreakSum = FormHistory.select(fn.SUM(LaborStatusForm.contractHours)).where( (FormHistory.historyType_id == "Labor Status Form ") & (FormHistory.status_id == "Approved"))

    totalBreakSum = (
    FormHistory
    .select(
        LaborStatusForm.department,
        LaborStatusForm.termCode.termCode,
        fn.SUM(LaborStatusForm.contractHours).alias('totalHours')
        
    )
    .join(
        LaborStatusForm,
        on=(FormHistory.formID == LaborStatusForm.laborStatusFormID),
    )
    .join(
        Term,
        on = (LaborStatusForm.termCode == Term.termCode)
    )
    .where(
        (FormHistory.historyType == "Labor Status Form") &
        (FormHistory.status == "Approved") &
        (LaborStatusForm.termCode == term)
    )
    .group_by(LaborStatusForm.department, LaborStatusForm.termCode).dicts()
)

    return totalBreakSum



# USED IN THE getActiveDepartmentsWithAllocation() FUNCTION
def getLSFCountPrimaries(currentTerm, department):
    """
    Returns the count of primary LSFs for a given department during a given term. (WIP)
    """
    lsfCountPrimaries = FormHistory.select().join(LaborStatusForm).join(Department).where(FormHistory.status == "Approved", LaborStatusForm.termCode == currentTerm.termCode, LaborStatusForm.jobType == "Primary", Department.departmentID == department.departmentID).count()
    return lsfCountPrimaries



# USED IN THE getActiveDepartmentsWithAllocation() FUNCTION
def getLSFCountSecondaries(currentTerm, department):
    """
    Returns the count of secondary LSFs for a given department during a given term. (WIP)
    """
    lsfCountSecondaries = FormHistory.select().join(LaborStatusForm).join(Department).where(FormHistory.status == "Approved", LaborStatusForm.termCode == currentTerm.termCode, LaborStatusForm.jobType == "Secondary", Department.departmentID == department.departmentID).count()
    return lsfCountSecondaries



def getActiveDepartmentsWithAllocation(term):
    """
    Returns a list of active departments with allocations for the given term.
    """

    # This was left just incase anything went wrong. Delete this if everything works as expected. Not necessary in current implementation.
    # activeDepartments = Department.select().where(Department.isActive == True)
    # allAllocations = Allocation.select().where(Allocation.termCode == currentAY)

    activeDepartments = (Department
                        .select(Department, Allocation)
                        .join(Allocation)
                        .where(
                            Department.isActive == True,
                            Allocation.termCode == term.termCode
                        )
                    )
    
    for dept in activeDepartments:
        dept.totalPrimaries = (dept.allocation.primary_10 + dept.allocation.primary_12 + dept.allocation.primary_15 + dept.allocation.primary_20)
        dept.totalSecondaries = (dept.allocation.secondary_5 + dept.allocation.secondary_10)

        dept.lsfCountPrimaries = getLSFCountPrimaries(term, dept)
        dept.lsfCountSecondaries = getLSFCountSecondaries(term, dept)

    return activeDepartments



def getAllocationStatus(term, department):
    """
    Returns the allocation status for a given department during a given term.
    """
    allocation = Allocation.get(
        (Allocation.termCode == term) &
        (Allocation.department == department)
    )
    return allocation.isFinal