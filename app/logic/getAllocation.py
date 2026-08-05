from datetime import date

from app.logic.allocationManager import getContractedAllocations, getTotalAllocations
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

    # allocationManager's helpers only look at the *final* Allocation row for the
    # term (they call getAllocation(..., isFinal=True) under the hood) and raise
    # if one doesn't exist yet. A department whose most recent term is still a
    # draft has no final row - fall back to the zeroed defaults above rather
    # than letting that propagate into a 500 on the department portal.
    try:
        result["allocated"] = getTotalAllocations(termCode, department.departmentID)["totalAllocations"]

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
        # getContractedAllocations' underlying SQL SUM() returns None (not 0)
        # for a department/term whose only approved forms are weekly-hours
        # ones (no break contract) - coalesce so the card doesn't render "None"
        result["breakHours"] = contractedAllocations["break_hours"] or 0
    except Allocation.DoesNotExist:
        pass

    return result
