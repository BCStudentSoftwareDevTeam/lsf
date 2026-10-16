from peewee import JOIN

from app.models.allocation import Allocation
from app.models.laborStatusForm import * 
from app.models.department import *
from app.models.term import *
from app.models.formHistory import FormHistory

ALLOCATION_BAND_FIELDS = [
    ('primary_10', 'Primary', 10),
    ('primary_12', 'Primary', 12),
    ('primary_15', 'Primary', 15),
    ('primary_20', 'Primary', 20),
    ('secondary_5', 'Secondary', 5),
    ('secondary_10', 'Secondary', 10),
]

band_labels = {fieldName: f"{hours} hour {jobType}" for fieldName, jobType, hours in ALLOCATION_BAND_FIELDS}


def getAllocation(termCode: int, dept: int, isFinal = True):
    '''
    This function returns a peewee object containing the selected allocation for given 
    department and term. If you want the pending allocation, pass in False for isFinal.
    '''
    try:
        academicYearCode = int(str(termCode)[:4] + "00")
        allocationObject = Allocation.select().where(
            Allocation.termCode.in_([termCode,academicYearCode]),
            Allocation.department == dept, 
            Allocation.isFinal == isFinal).dicts().get()
        return allocationObject 
    except:
        return 0 


def getTotalAllocations(termCode: int, dept: int):
    '''
    This function returns a dictionary representation of the given department's allocation for the given term.
    '''
    try:
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
    except:
        allocationDict = {"primary_10": "",
                    "primary_12": "",
                    "primary_15": "",
                    "primary_20": "",
                    "secondary_5": "",
                    "secondary_10": "", 
                    "breakHours": "No Allocations Found", 
                    "totalPrimaries": "", 
                    "totalSecondaries": "",
                    "totalAllocations": "No Allocations Found"}
    return allocationDict 

def countContracts(jobType: str, weeklyContractHours: int, termCode: int, dept: int, AYtermCode: int = None):
    '''
    This function counts the number of positions of a given type in a given department.
    For example, countContracts('secondary', 5, 202511, 1) returns the number of secondary 
    5-hour positions in the CS department for the 2025 Fall term.
    '''
    academicYearCode = int(str(termCode)[:4] + "00") 

    # This sets the date condition to determine whether the form is within the boundaries of the term
    # Fall only contracts end before spring, spring contracts start after fall.
    fallMonths = ["07","08","09","10","11","12"]
    springMonths = ["01","02","03","04","05","06"]
    if str(termCode).endswith("11"):
        dateCondition = (
            (LaborStatusForm.endDate.month.in_(fallMonths)) |
            (LaborStatusForm.startDate.month.in_(fallMonths) & # Reused check for year-long positions
                LaborStatusForm.endDate.month.in_(springMonths))
            )
    elif str(termCode).endswith("12"):
        dateCondition = (
            (LaborStatusForm.startDate.month.in_(springMonths)) |
            (LaborStatusForm.startDate.month.in_(fallMonths) &
                LaborStatusForm.endDate.month.in_(springMonths))
            )
    else:
        dateCondition = (
            (LaborStatusForm.startDate.month.in_(fallMonths) &
                LaborStatusForm.endDate.month.in_(springMonths))
            )

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
                                dateCondition,
                            ).count()
    return lsfCountPositions 

def getContractedAllocations(termCode: int, dept: int):
    '''
    This function returns a dictionary with a breakdown of all types of contracts
    for the given department and term in the form of a dictionary.
    '''
    academicYearCode = int(str(termCode)[:4] + "00")
    breakHoursTotal = (
        FormHistory.select(fn.SUM(LaborStatusForm.contractHours))
        .join(LaborStatusForm, on=(FormHistory.formID == LaborStatusForm.laborStatusFormID))
        .where(
            FormHistory.historyType == "Labor Status Form",
            FormHistory.status == "Approved",
            LaborStatusForm.termCode.in_([termCode, academicYearCode]),
            LaborStatusForm.department == dept,
        )
        .scalar()
    ) or 0

    # dictionary definition:
    usedPositions = {
    "used_10": countContracts("Primary", "10", termCode, dept),
    "used_12": countContracts("Primary", "12", termCode, dept),
    "used_15": countContracts("Primary", "15", termCode, dept),
    "used_20": countContracts("Primary", "20", termCode, dept),
    "used_5_sec": countContracts("Secondary", "5", termCode, dept),
    "used_10_sec": countContracts("Secondary", "10", termCode, dept),
    "used_primaries": 0,
    "used_secondaries": 0,
    "used_total": 0,  # all contracts with weekly hours, i.e. primaries + secondaries (not break contracts)
    "break_hours": breakHoursTotal  # all break hours contracted (but not necessarily worked)
    }
    usedPositions["used_primaries"] = sum(list(usedPositions.values())[:4])
    usedPositions["used_secondaries"] = sum(list(usedPositions.values())[4:6])
    usedPositions["used_total"] = sum(list(usedPositions.values())[:6])
    return usedPositions

def getBreakContracts(termCode, dept):
    break_allocation = FormHistory.select(fn.SUM(LaborStatusForm.contractHours)
    ).join(LaborStatusForm
    ).where(
        FormHistory.historyType == "Labor Status Form",
        FormHistory.status.in_(["Approved", "Pending", "Pre-Student Approval"]),
        LaborStatusForm.termCode == termCode,
        LaborStatusForm.department == dept,
        LaborStatusForm.contractHours.is_null(False)).scalar()
    if break_allocation != None:
        return break_allocation
    else:
        return 0

def getAllocationSummary(dept, term):
    summary = {
        'allocation': None,
        'allocationBands': None,
        'totalPositionsAllocated': None,
        'totalPositionsUsed': None,
        'breakHoursUsed': None,
    }

    if not (dept and term):
        return summary

    # A department can have both a draft and a final allocation for a term; prefer the final one.
    allocation = (Allocation.select()
                  .where(Allocation.department == dept, Allocation.termCode == term)
                  .order_by(Allocation.isFinal.desc())
                  .first())
    summary['allocation'] = allocation
    if not allocation:
        return summary

    allocationBands = {}
    for fieldName, jobType, hours in ALLOCATION_BAND_FIELDS:
        used = (LaborStatusForm
                .select()
                .join(FormHistory, on=(FormHistory.formID == LaborStatusForm.laborStatusFormID))
                .where(LaborStatusForm.department == dept,
                       LaborStatusForm.termCode == term,
                       LaborStatusForm.jobType == jobType,
                       LaborStatusForm.weeklyHours == hours,
                       FormHistory.historyType == "Labor Status Form",
                       ~(FormHistory.status % "Denied%"))
                .distinct()
                .count())
        allocationBands[fieldName] = {'used': used, 'allocated': getattr(allocation, fieldName)}

    summary['allocationBands'] = allocationBands
    summary['totalPositionsAllocated'] = sum(band['allocated'] for band in allocationBands.values())
    summary['totalPositionsUsed'] = sum(band['used'] for band in allocationBands.values())

    # Break hours are tracked on separate break-term rows (e.g. Thanksgiving Break)
    # that share the same academic year prefix as the given AY term.
    yearPrefix = str(term.termCode)[:-2]
    breakTermCodes = [t.termCode for t in Term.select().where(Term.isBreak == True)
                      if str(t.termCode).startswith(yearPrefix)]
    summary['breakHoursUsed'] = (LaborStatusForm
                                 .select(fn.SUM(LaborStatusForm.contractHours))
                                 .join(FormHistory, on=(FormHistory.formID == LaborStatusForm.laborStatusFormID))
                                 .where(LaborStatusForm.department == dept,
                                        LaborStatusForm.termCode.in_(breakTermCodes),
                                        FormHistory.historyType == "Labor Status Form",
                                        ~(FormHistory.status % "Denied%"))
                                 .scalar()) or 0

    return summary


def getAllocationWarningForTermCode(dept, termCode):
    """ Allocations are stored on the academic-year term (ending in 00), so terms like
    Fall, Spring, or a break term fall back to their academic year's allocation. """
    if not (dept and termCode):
        return None
    ayTermCode = str(termCode)[:-2] + '00'
    for code in (str(termCode), ayTermCode):
        term = Term.get_or_none(Term.termCode == code)
        warning = getAllocationWarning(dept, term) if term else None
        if warning:
            return warning
    return None


def getAllocationWarning(dept, term):
    summary = getAllocationSummary(dept, term)
    if not summary['allocation']:
        return None

    positionsRemaining = summary['totalPositionsAllocated'] - summary['totalPositionsUsed']
    breakHoursRemaining = summary['allocation'].breakHours - summary['breakHoursUsed']

    # A department can be within its total position count while still exceeding
    # one specific hour-band (e.g. over on 10-hour Primary but under on others),
    # so each band needs to be checked individually, not just the aggregate total.
    overAllocatedBands = [
        {'label': band_labels[fieldName], 'used': band['used'], 'allocated': band['allocated']}
        for fieldName, band in summary['allocationBands'].items()
        if band['used'] > band['allocated']
    ]
    isPositionsTotalOverAllocated = positionsRemaining < 0
    isPositionsOverAllocated = isPositionsTotalOverAllocated or bool(overAllocatedBands)
    isBreakHoursOverAllocated = breakHoursRemaining < 0

    return {
        'departmentName': dept.DEPT_NAME,
        'totalPositionsAllocated': summary['totalPositionsAllocated'],
        'totalPositionsUsed': summary['totalPositionsUsed'],
        'positionsRemaining': positionsRemaining,
        'isPositionsOverAllocated': isPositionsOverAllocated,
        'isPositionsTotalOverAllocated': isPositionsTotalOverAllocated,
        'overAllocatedBands': overAllocatedBands,
        'breakHoursAllocated': summary['allocation'].breakHours,
        'breakHoursUsed': summary['breakHoursUsed'],
        'breakHoursRemaining': breakHoursRemaining,
        'isBreakHoursOverAllocated': isBreakHoursOverAllocated,
        'isOverAllocated': isPositionsOverAllocated or isBreakHoursOverAllocated,
    }


