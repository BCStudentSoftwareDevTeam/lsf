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

from playhouse.shortcuts import model_to_dict



def generateAdjacentYears(academicYearTermCode=None): 
    """
    Generates the current, and the following academic years. 
    """
    currentYear      = g.openTerm.termCode // 100
    nextYear         = currentYear + 1

    currentAYCode    = currentYear * 100
    nextAYCode       = nextYear * 100

    # Admins cannot view allocations for the years that are beyond the current, the previous, or the following academic year 
    if academicYearTermCode not in (None, currentAYCode, nextAYCode):
        abort(400)


    currentAY, _  = Term.get_or_create(
        termCode=currentAYCode,
        defaults={"termName": "AY {}-{}".format(currentYear, currentYear + 1), "isAcademicYear": True}
        )

    nextAY, _     = Term.get_or_create(
        termCode=nextAYCode,
        defaults={"termName": "AY {}-{}".format(nextYear, nextYear + 1), "isAcademicYear": True}
    )

    return (currentAY, nextAY)




####################################################################################################################################
# Everything below this line will eventually be deleted  


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



def getActiveDepartmentsWithAllocation(term,isFinal = True):
    """
    Returns a list of active departments with allocations for the given term.
    """

    # This was left just incase anything went wrong. Delete this if everything works as expected. Not necessary in current implementation.
    # activeDepartments = Department.select().where(Department.isActive == True)
    # allAllocations = Allocation.select().where(Allocation.termCode == currentAY)

    activeDepartments = (Allocation
                        .select(Department, Allocation)
                        .join(Department)
                        .where(
                            Department.isActive == True,
                            Allocation.termCode == term.termCode,
                            Allocation.isFinal == isFinal,
                            )
                    )
    
  
    for allocation in activeDepartments:
        allocation.totalPrimaries = (allocation.primary_10 + allocation.primary_12 + allocation.primary_15 + allocation.primary_20)
        allocation.totalSecondaries = (allocation.secondary_5 + allocation.secondary_10)

        if isFinal:            # do not need to count them for requested allocations
            allocation.lsfCountPrimaries = getLSFCountPrimaries(term, allocation.department)
            allocation.lsfCountSecondaries = getLSFCountSecondaries(term, allocation.department)
  
    return activeDepartments


def getActiveDepartmentsAllocations(term,nextTerm):
    """
    This function gets active departments, active allocations for the current AY and future AY.
    It returns a dictionary which contains three objects grouped by the departmentID
    """

    activeDepartments = Department.select().where(Department.isActive == True)  

    allocations = getActiveDepartmentsWithAllocation(term)

    allocByDeptId = {}

    # index allocations by department ID
    for alloc in allocations:
        allocByDeptId[alloc.department.departmentID] = alloc

    requestedAllocations = getActiveDepartmentsWithAllocation(nextTerm, False) 

    # index requested allocations by department ID
    reqAllocByDeptId = {}
    for alloc in requestedAllocations:
        reqAllocByDeptId[alloc.department.departmentID] = alloc

    # build combined dictionary for active departments
    activeDepartmentsAllocations = {}

    for dept in activeDepartments:
        activeDepartmentsAllocations[dept.departmentID] = {
        "department": dept,
        "allocation": allocByDeptId.get(dept.departmentID),  # None if no allocation
        "requestedAllocation": reqAllocByDeptId.get(dept.departmentID),  # None if no requested allocation
    }
    return activeDepartmentsAllocations


def getAllocationStatus(term, department):
    """
    Returns the allocation status for a given department during a given term.
    """
    allocation = Allocation.get(
        (Allocation.termCode == term) &
        (Allocation.department == department)
    )
    return allocation.isFinal






# THE FUNCTIONS BELOW ARE NO LONGER USED IN THE CODE (BECAUSE WE CAN ONLY CHOOSE AN ACADEMIC YEAR IN THE CODE). 
# IF SOMETHING CHANGES,YOU CAN USE THE CODE BELOW

# # USED IN THE generateTermsForAdjacentYears() FUNCTION
# def generateTerms(termCode):
#     """
#     Generates all the terms in an academic year. 
#     """

#     # Truncating term codes to hundreds. That's how we get the academic year. 
#     academicYearCode = (termCode // 100)
    
#     return createTerms(academicYearCode)   



# def generateTermsForAdjacentYears(academicYear): 
#     """
#     Generates all the terms for the current, the previous, and the future academic years. 
#     """

#     previousAYCode  = g.openTerm.termCode - 100
#     currentAYCode   = g.openTerm.termCode 
#     nextATCode      = g.openTerm.termCode + 100

#     if (academicYear != previousAYCode) and (academicYear != currentAYCode) and (academicYear != nextATCode):
#         abort(400)

#     PreviousAYTerms    = generateTerms(previousAYCode)
#     CurrentAYTerms     = generateTerms(currentAYCode) 
#     NextAYTerms        = generateTerms(nextATCode)

#     return (PreviousAYTerms, CurrentAYTerms, NextAYTerms)