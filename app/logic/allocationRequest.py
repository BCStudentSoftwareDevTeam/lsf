from flask import request, g
from app.models.allocation import Allocation
from app.logic.allocationManager import *

def belongsToDepartment(department):
    """
    Checks whether the current user is a supervisor who belongs to a certain department.
    """
    return SupervisorDepartment.select().where((SupervisorDepartment.supervisor == g.currentUser.supervisor) & (SupervisorDepartment.department == department.departmentID)).exists()


def getOrUpdateRequestedAllocation():
    """
    Gets or updates the requested allocation (used for the Allocation Request page specificially). 
    """
    currentAY = (g.openTerm.termCode // 100) * 100                          # current academic year
    nextAY = currentAY + 100                                                # upcoming (next) academic year

    requester = request.form.get("submitter", type=int, default=None)       # the requesting department

    currentAlloc = getAllocation(g.openTerm.termCode, requester, True)      # the current allocation 

    # the list of the fields updated after submitting the allocation request
    updatedFields = {
        "termCode": nextAY, 
        "department": request.form.get("submitter", type=int, default=None), 
        "isFinal": False,
        "justification": request.form.get("justification", default=""),
        "primary_10": request.form.get("primary_10", type=int, default=currentAlloc["primary_10"]),
        "primary_12": request.form.get("primary_12", type=int, default=currentAlloc["primary_12"]),
        "primary_15": request.form.get("primary_15", type=int, default=currentAlloc["primary_15"]),
        "primary_20": request.form.get("primary_20", type=int, default=currentAlloc["primary_20"]),
        "secondary_5": request.form.get("secondary_5", type=int, default=currentAlloc["secondary_5"]),
        "secondary_10": request.form.get("secondary_10", type=int, default=currentAlloc["secondary_10"]),
        "breakHours": request.form.get("breakHours", type=int, default=currentAlloc["breakHours"])
    }

    # saving the newly approved allocation
    requestedAlloc, wasCreated = Allocation.get_or_create(termCode=nextAY, department=requester, isFinal=False, defaults={**updatedFields})
    
    if not wasCreated: # if the allocation has already existed (it is being resubmitted/updated)
        for key, value in updatedFields.items():
            setattr(requestedAlloc, key, value) # updating all the fields based on updatedFields values
    
    requestedAlloc.save()