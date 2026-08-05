from datetime import date

from app.logic.allocationManager import getContractedAllocations
from app.models.allocation import Allocation
from app.models.term import Term


def getCurrentSemesterLabel(term):
    """Return the Fall/Spring label (e.g. "Fall 2025") for the AY term's
    current semester, picking the season from today's month."""
    if not term:
        return None
    academicYear = int(str(term.termCode)[:4])
    if date.today().month >= 8:
        return f"Fall {academicYear}"
    return f"Spring {academicYear + 1}"


def getDepartmentAllocationSummary(department):
    """Return allocation-utilization values for a department's most recent term."""
    result = {
        "term": None,
        "currentSemester": None,
        "allocated": 0,
        "used": 0,
        "usedPositions": {
            "used10": 0,
            "used12": 0,
            "used15": 0,
            "used20": 0,
            "usedSecondary5": 0,
            "usedSecondary10": 0,
        },
        "breakHours": 0,
    }

    departmentAllocations = list(
        Allocation.select(Allocation, Term).join(Term).where(Allocation.department == department)
    )
    if not departmentAllocations:
        return result

    recentTerm = Term.order_by_term([a.termCode for a in departmentAllocations], reverse=True)[0]
    termCode = recentTerm.termCode
    result["term"] = recentTerm
    result["currentSemester"] = getCurrentSemesterLabel(recentTerm)

    # "allocated" is summed directly from the rows already fetched above rather
    # than through allocationManager's getTotalAllocations, since that only
    # looks at the *final* Allocation row for a term - a department whose most
    # recent term is still a draft (isFinal=False, no final row yet) would
    # otherwise show 0 allocated instead of its draft numbers.
    recentTermAllocations = [a for a in departmentAllocations if a.termCode_id == termCode]
    result["allocated"] = sum(
        a.primary_10 + a.primary_12 + a.primary_15 + a.primary_20 + a.secondary_5 + a.secondary_10
        for a in recentTermAllocations
    )

    contractedAllocations = getContractedAllocations(termCode, department.departmentID)
    result["used"] = contractedAllocations["used_total"]
    result["usedPositions"] = {
        "used10": contractedAllocations["used_10"],
        "used12": contractedAllocations["used_12"],
        "used15": contractedAllocations["used_15"],
        "used20": contractedAllocations["used_20"],
        "usedSecondary5": contractedAllocations["used_5_sec"],
        "usedSecondary10": contractedAllocations["used_10_sec"],
    }
    result["breakHours"] = contractedAllocations["break_hours"]

    return result
