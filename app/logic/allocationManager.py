from app.models.allocation import Allocation
from app.models.laborStatusForm import * 
from app.models.department import *
from app.models.term import *
from app.models.formHistory import FormHistory
from peewee import JOIN


def getAllocation(termCode, dept):
        allocationObject = Allocation.select().where(
            Allocation.termCode == termCode,
            Allocation.department == dept, 
            Allocation.isFinal == True).dicts().get()
        return allocationObject


def getAllocationNonFinal(termCode, dept):
        allocationObject = Allocation.select().where(
            Allocation.termCode == termCode,
            Allocation.department == dept, 
            Allocation.isFinal == False).dicts().get()
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
                    "totalSecondaries": (allocationObject["secondary_5"] + allocationObject["secondary_10"]),
                    "totalAllocations": (allocationObject["primary_10"] + allocationObject["primary_12"] + allocationObject["primary_15"] + allocationObject["primary_20"] + allocationObject["secondary_5"] + allocationObject["secondary_10"] )}
    return allocationDict
 
def countContracts(jobType, weeklyContractHours, termCode, dept):
    lsfCountPrimaries = FormHistory.select(
                            ).join(LaborStatusForm
                            ).join(Department
                            ).where(
                                FormHistory.status.in_(["Approved", "Pending", "Pre-Student Approval"]),
                                LaborStatusForm.termCode == termCode,
                                LaborStatusForm.jobType == jobType,
                                LaborStatusForm.weeklyHours == weeklyContractHours,
                                Department.departmentID == dept,
                            ).count()
    return lsfCountPrimaries

def getContractedAllocations(termCode, dept):
    allocationObject = getAllocation(termCode, dept)
    break_allocation = FormHistory.select(
        LaborStatusForm.department,
        LaborStatusForm.termCode.termCode,
        fn.SUM(LaborStatusForm.contractHours).alias('totalHours')
    ).join(
        LaborStatusForm,
        on=(FormHistory.formID == LaborStatusForm.laborStatusFormID),
    ).join(
        Term,
        on = (LaborStatusForm.termCode == Term.termCode)
    ).where(
        (FormHistory.historyType == "Labor Status Form") &
        (FormHistory.status == "Approved") &
        (LaborStatusForm.termCode == termCode)
    ).group_by(
        LaborStatusForm.department, 
        LaborStatusForm.termCode).dicts()
    
    breakSum = {"totalHours": 0}
    if dept:
        for row in break_allocation:
            if row["department"] == dept.departmentID:
                breakSum = row
                break

    usedPositions = {
    "used_10": countContracts("Primary", "10", termCode, dept),
    "used_12": countContracts("Primary", "12", termCode, dept),
    "used_15": countContracts("Primary", "15", termCode, dept),
    "used_20": countContracts("Primary", "20", termCode, dept),
    "used_5_sec": countContracts("Secondary", "5", termCode, dept),
    "used_10_sec": countContracts("Secondary", "10", termCode, dept),
    "usedTotal": 0,
    "break_hours": breakSum["totalHours"]
    }
    usedPositions["usedTotal"] = sum(list(usedPositions.values())[:7])
    return usedPositions