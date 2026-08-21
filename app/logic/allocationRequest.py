from flask import request, g
from app.models.allocation import Allocation
from app.logic.allocationManager import *
from app.logic.academicYearManager import getCurrentAndNextAY


def getOrUpdateRequestedAllocation():
    """
    Gets or updates the requested allocation (used for the Allocation Request page specificially). 
    """
    currentAY, nextAY = getCurrentAndNextAY()

    requester = request.form.get("submitter", type=int, default=None)       # the requesting department

    # the list of the fields updated after submitting the allocation request
    updatedFields = {
        "termCode": nextAY, 
        "department": requester, 
        "isFinal": False,
        "justification": request.form.get("justification", default=""),
        "primary_10": request.form.get("primary_10", type=int, default=None),
        "primary_12": request.form.get("primary_12", type=int, default=None),
        "primary_15": request.form.get("primary_15", type=int, default=None),
        "primary_20": request.form.get("primary_20", type=int, default=None),
        "secondary_5": request.form.get("secondary_5", type=int, default=None),
        "secondary_10": request.form.get("secondary_10", type=int, default=None),
        "breakHours": request.form.get("breakHours", type=int, default=None)
    }

    # saving the newly approved allocation
    requestedAlloc, wasCreated = Allocation.get_or_create(termCode=nextAY, department=requester, isFinal=False, defaults={**updatedFields})
    
    if not wasCreated: # if the allocation has already existed (it is being resubmitted/updated)
        for key, value in updatedFields.items():
            setattr(requestedAlloc, key, value) # updating all the fields based on updatedFields values
    
    requestedAlloc.save()