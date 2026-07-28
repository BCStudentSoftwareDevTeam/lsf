from app.models.allocation import Allocation
from app.models.laborStatusForm import * 
from app.models.department import *
from app.models.term import *
from app.models.formHistory import FormHistory


def getAllocation(termCode, dept):
    allocationObject = Allocation.select().where(
        Allocation.termCode == 202500,
        Allocation.department == 3, 
        Allocation.isFinal == True).dicts().get() #FIXME
    return allocationObject

def getTotalAllocations(termCode, dept):
    allocationObject = getAllocation(termCode, dept)
    allocationDict = {"primary_10": allocationObject["primary_10"],
                    "primary_12": allocationObject["primary_12"],
                    "primary_15": allocationObject["primary_15"],
                    "primary_20": allocationObject["primary_20"],
                    "secondary_5": allocationObject["secondary_5"],
                    "secondary_10": allocationObject["secondary_10"],
                    "breakHours": allocationObject["breakHours"],
                    "totalPrimaries": (allocationObject["primary_10"] + allocationObject["primary_12"] + allocationObject["primary_15"] + allocationObject["primary_20"]),
                    "totalSecondaries": (allocationObject["secondary_5"] + allocationObject["secondary_10"]) }
    return allocationDict
 
def countContracts(jobType, contractHours):
    return FormHistory.select().join(LaborStatusForm).where(
                                                            (FormHistory.status == "Pending" or 
                                                            FormHistory.status == "Approved" or 
                                                            FormHistory.status == "Pre-Student-Approval"),
                                                            LaborStatusForm.department == 1,
                                                            LaborStatusForm.termCode == 202500, #FIXME
                                                            LaborStatusForm.jobType == jobType,
                                                            LaborStatusForm.weeklyHours == contractHours,
                                                            LaborStatusForm.contractHours.is_null(True)).count()
    return LaborStatusForm.select().where(
        LaborStatusForm.department == 1,
        LaborStatusForm.termCode == 202500, #FIXME
        LaborStatusForm.jobType == jobType,
        LaborStatusForm.weeklyHours == contractHours,
        LaborStatusForm.contractHours.is_null(True)).count()


def getContractedAllocations(termCode, dept):
    allocationObject = getAllocation(termCode, dept)
    # usedPrimariesAllocation = [hours for hours in LaborStatusForm.select(LaborStatusForm.weeklyHours).where(LaborStatusForm.department == dept, LaborStatusForm.termCode == 202500, LaborStatusForm.contractHours.is_null(True), LaborStatusForm.jobType == "Primary")]
    break_allocation = LaborStatusForm.select(LaborStatusForm.contractHours).where(LaborStatusForm.department == dept, LaborStatusForm.termCode == 202500, LaborStatusForm.contractHours.is_null(False))
    breakSum = int(sum(form.contractHours or 0 for form in break_allocation))
    usedPositions = {
    "used_10": countContracts("Primary", "10"),
    "used_12": countContracts("Primary", "12"),
    "used_15": countContracts("Primary", "15"),
    "used_20": countContracts("Primary", "20"),
    "used_5_sec": countContracts("Secondary", "5"),
    "used_10_sec": countContracts("Secondary", "10"),
    "break_hours": breakSum
    }
    return usedPositions