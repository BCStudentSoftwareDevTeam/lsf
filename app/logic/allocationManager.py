from app.models.allocation import Allocation
from app.models.laborStatusForm import * 
from app.models.department import *
from app.models.term import *
from app.models.formHistory import FormHistory
from peewee import JOIN


def getAllocation(termCode: int, dept: int):
    academicYearCode = int(str(termCode)[:5] + "00")
    allocationObject = Allocation.select().where(
        Allocation.termCode.in_([termCode,academicYearCode]),
        Allocation.department == dept, 
        Allocation.isFinal == True).dicts().get()
    return allocationObject # returns peewee object containing the current allocation for given department


def getAllocationNonFinal(termCode: int, dept: int):
    academicYearCode = int(str(termCode)[:5] + "00")
    allocationObject = Allocation.select().where(
        Allocation.termCode.in_([termCode,academicYearCode]),
        Allocation.department == dept, 
        Allocation.isFinal == False).dicts().get()
    return allocationObject # returns peewee object containing the pending allocation for given department (I think?)


def getTotalAllocations(termCode: int, dept: int):
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


def countContracts(jobType: str, weeklyContractHours: int, termCode: int, dept: int):
    '''
    This function counts the number of positions of a given type in a given department.
    For example, countContracts('secondary', 5, 202511, 1) returns the number of secondary 
    5-hour positions in the CS department for the 2025 Fall term.
    '''
    academicYearCode = int(str(termCode)[:5] + "00") 
    lsfCountPositions = FormHistory.select(
                            ).join(LaborStatusForm
                            ).join(Department
                            ).where(
                                FormHistory.historyType == "Labor Status Form",
                                FormHistory.status.in_(["Approved", "Pending", "Pre-Student Approval"]),
                                LaborStatusForm.termCode.in_([termCode,academicYearCode]),
                                LaborStatusForm.jobType == jobType, # 'primary' or 'secondary'
                                LaborStatusForm.weeklyHours == weeklyContractHours, # 5, 10, 12, 15, or 20
                                Department.departmentID == dept,
                            ).count()
    return lsfCountPositions 


def getContractedAllocations(termCode: int, dept: int):
    '''
    This function returns a dictionary with a breakdown of all types of contracts 
    for the given department and term in the form of a dictionary.
    '''
    academicYearCode = int(str(termCode)[:5] + "00")
    allocationObject = getAllocation(termCode, dept)
    break_allocation = FormHistory.select(
        LaborStatusForm.department,
        LaborStatusForm.termCode,
        fn.SUM(LaborStatusForm.contractHours).alias('total_hours')
    ).join(
        LaborStatusForm,
        on=(FormHistory.formID == LaborStatusForm.laborStatusFormID),
    ).join(
        Term,
        on = (LaborStatusForm.termCode == Term.termCode )
    ).where(
        (FormHistory.historyType == "Labor Status Form") &
        (FormHistory.status == "Approved") & 
        (LaborStatusForm.termCode.in_([termCode,academicYearCode]))
    ).group_by(
        LaborStatusForm.department, 
        LaborStatusForm.termCode).dicts()
    
    breakSum = {"total_hours": 0}
    if dept:
        for row in break_allocation:
            if row["department"] == dept:
                breakSum = row
                break
    
    # dictionary definition:
    usedPositions = {
    "used_10": countContracts("Primary", "10", termCode, dept),
    "used_12": countContracts("Primary", "12", termCode, dept),
    "used_15": countContracts("Primary", "15", termCode, dept),
    "used_20": countContracts("Primary", "20", termCode, dept),
    "used_5_sec": countContracts("Secondary", "5", termCode, dept),
    "used_10_sec": countContracts("Secondary", "10", termCode, dept),
    "used_total": 0,  # all contracts with weekly hours, i.e. primaries + secondaries (not break contracts)
    "break_hours": breakSum["total_hours"]  # all break hours contracted (but not necessarily worked)
    }
    usedPositions["used_total"] = sum(list(usedPositions.values())[:7])
    return usedPositions