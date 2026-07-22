from app.controllers.admin_routes.termManagement import createTerms
from app.models.laborStatusForm import *
from app.models.formHistory import *
from app.models.allocation import *
from app.models.department import *
from app.models.term import *
from app.login_manager import require_login
from app.controllers.main_routes import departmentPortal
from flask import g, abort, render_template
from peewee import fn


def checkAdmistratorRights():
    """
    Checks whether the current user has administrator rights to view the page.  
    """
    currentUser = require_login()

    if not currentUser:                    # If the current user is not logged in
        return render_template('errors/403.html')

    if currentUser.isLaborAdmin:       # If the currrent user is an admin
        return "", 500
    else: 
        if currentUser.student: # If the currrent user is logged in as a student
            return redirect('/laborHistory/' + currentUser.student.ID)
        elif currentUser.supervisor:
            return render_template('errors/403.html'), 403

    



def getUsedBreakHours(term):
    """
    Returns the total number of break hours used by each department for a given term.
    """
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
    
    print(list(totalBreakSum))
    
    # correctLSF = LaborStatusForm.select().where(LaborStatusForm.termCode == term)

    # print("Something2\n\n\n\n",list(correctLSF))

    return totalBreakSum



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

        # # print("######################")
        # print(f"COUNTS: {lsfCountSecondaries} ")
        # print([lsf.formID for lsf in lsfCountPrimaries])
        # print([lsf.formID for lsf in lsfCountSecondaries])

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



def getLSFCountPrimaries(currentTerm, department):
    """
    Returns the count of primary LSFs for a given department during a given term. (WIP)
    """
    lsfCountPrimaries = FormHistory.select().join(LaborStatusForm).join(Department).where(FormHistory.status == "Approved", LaborStatusForm.termCode == currentTerm.termCode, LaborStatusForm.jobType == "Primary", Department.departmentID == department.departmentID).count()
    return lsfCountPrimaries



def getLSFCountSecondaries(currentTerm, department):
    """
    Returns the count of secondary LSFs for a given department during a given term. (WIP)
    """
    lsfCountSecondaries = FormHistory.select().join(LaborStatusForm).join(Department).where(FormHistory.status == "Approved", LaborStatusForm.termCode == currentTerm.termCode, LaborStatusForm.jobType == "Secondary", Department.departmentID == department.departmentID).count()
    return lsfCountSecondaries



# def getTotalPositionHours



# def getCurrentSelectedTerm(currentTerm):
    #'''
    #Returns the current term code based on a the selected term from a dropdown menu in the manage departments page.
    #Should only contain the current term, the next term, and the previous term.
    #'''



def generateTerms(termCode):
    """
    Generates all the terms in an academic year. 
    """

    # Truncating term codes to hundreds. That's how we get the academic year. 
    academicYearCode = (termCode // 100)
    
    return createTerms(academicYearCode)   



def generateTermsForAdjacentYears(academicYear): 
    """
    Generates all ther terms for the current year, the previous year, and the future year. 
    """


    previousAYCode  = g.openTerm.termCode - 100
    currentAYCode   = g.openTerm.termCode 
    nextATCode      = g.openTerm.termCode + 100

    if (academicYear != previousAYCode) and (academicYear != currentAYCode) and (academicYear != nextATCode):
        abort(400)

    PreviousAYTerms    = generateTerms(previousAYCode)
    CurrentAYTerms     = generateTerms(currentAYCode) 
    NextAYTerms        = generateTerms(nextATCode)

    return (PreviousAYTerms, CurrentAYTerms, NextAYTerms)
