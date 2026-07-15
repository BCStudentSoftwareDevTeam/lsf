from app.models.laborStatusForm import *
from app.models.formHistory import *
from app.models.allocation import *
from app.models.department import *
from app.models.term import *
from app.controllers.main_routes import departmentPortal
from peewee import fn


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


def getActiveDepartmentsWithAllocation(currentTerm):
    """
    Returns a list of active departments that have an allocation for the given term.
    """
    activeDep = (Department
                        .select(Department, Allocation)
                        .join(Allocation)
                        .where(
                            Department.isActive == True,
                            Allocation.termCode == currentTerm.termCode
                        )
                    )
    return activeDep

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
    