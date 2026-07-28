from app.models.allocation import Allocation
from app.models.laborStatusForm import * 
from app.models.department import *
from app.models.term import *
from app.models.formHistory import FormHistory
from peewee import JOIN


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
                    "totalSecondaries": (allocationObject["secondary_5"] + allocationObject["secondary_10"]),
                    "totalAllocations": (allocationObject["primary_10"] + allocationObject["primary_12"] + allocationObject["primary_15"] + allocationObject["primary_20"] + allocationObject["secondary_5"] + allocationObject["secondary_10"] )}
    return allocationDict
 
def countContracts(jobType, contractHours, termCode, dept):
    lsfCountPrimaries = FormHistory.select().join(LaborStatusForm).join(Department).where((FormHistory.status == "Approved" |
                                                                                          FormHistory.status == "Pending" |
                                                                                          FormHistory.status == "Pre-Student Approval"),
                                                                                          LaborStatusForm.termCode == termCode,
                                                                                          LaborStatusForm.jobType == jobType,
                                                                                          FormHistory.formID.weeklyHours == contractHours,
                                                                                          Department.departmentID == dept).count()
    return lsfCountPrimaries
    return LaborStatusForm.select().where(
        LaborStatusForm.department == 1,
        LaborStatusForm.termCode == 202500, #FIXME
        LaborStatusForm.jobType == jobType,
        LaborStatusForm.weeklyHours == contractHours,
        LaborStatusForm.contractHours.is_null(True)).count()


def getContractedAllocations(termCode, dept):
    allocationObject = getAllocation(termCode, dept)
    # usedPrimariesAllocation = [hours for hours in LaborStatusForm.select(LaborStatusForm.weeklyHours).where(LaborStatusForm.department == dept, LaborStatusForm.termCode == 202500, LaborStatusForm.contractHours.is_null(True), LaborStatusForm.jobType == "Primary")]
    # break_allocation = LaborStatusForm.select(LaborStatusForm.contractHours).where(LaborStatusForm.department == dept, LaborStatusForm.termCode == 202500, LaborStatusForm.contractHours.is_null(False))

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
        (LaborStatusForm.termCode == "202500")
    ).group_by(
        LaborStatusForm.department, 
        LaborStatusForm.termCode).dicts()
    
    print("\n\n\n\n\n\n\n\n\nasdf")
    print(type(break_allocation[0]))
    # breakSum = int(sum(form.contractHours or 0 for form in break_allocation))
    # print(breakSum)
    breakSum = {"totalHours": 0}
    for row in break_allocation:
        if row["department"] == dept.departmentID:
            breakSum = row
            break

    print("\n\n\n\n\n\n" + str(list(break_allocation)))
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
    print(f" faahhh \n\n\n\n\n {list(usedPositions.values())[:7]}")
    usedPositions["usedTotal"] = sum(list(usedPositions.values())[:7])
    return usedPositions