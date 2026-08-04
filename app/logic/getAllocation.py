from datetime import date

from peewee import fn

from app.models.allocation import Allocation
from app.models.laborStatusForm import LaborStatusForm
from app.models.term import Term
from app.models.formHistory import FormHistory


def getCurrentSemesterLabel(term):
    """Return the Fall/Spring label (e.g. "Fall 2025") for the AY term's
    current semester, picking the season from today's month."""
    if not term:
        return None
    academicYear = int(str(term.termCode)[:4])
    if date.today().month >= 8:
        return f"Fall {academicYear}"
    return f"Spring {academicYear + 1}"


def countWorkers(department, termCode, jobType, hoursBucket):
    workerCount = (
        LaborStatusForm.select()
        .join(FormHistory, on=(FormHistory.formID == LaborStatusForm.laborStatusFormID))
        .where(
            LaborStatusForm.department == department,
            LaborStatusForm.termCode == termCode,
            LaborStatusForm.jobType == jobType,
            LaborStatusForm.weeklyHours == hoursBucket,
            LaborStatusForm.contractHours.is_null(True),
            FormHistory.historyType == "Labor Status Form",
            ~(FormHistory.status % "Denied%"),
        )
        .count()
    )
    return workerCount


def getBreakHours(department, termCode):
    breakHoursTotal = (
        LaborStatusForm.select(fn.SUM(LaborStatusForm.contractHours))
        .join(FormHistory, on=(FormHistory.formID == LaborStatusForm.laborStatusFormID))
        .where(
            LaborStatusForm.department == department,
            LaborStatusForm.termCode == termCode,
            FormHistory.historyType == "Labor Status Form",
            FormHistory.status == "Approved",
        )
        .scalar()
    ) or 0
    return breakHoursTotal


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

    totalPositions = (
        Allocation.select(
            fn.SUM(Allocation.primary_10)
            + fn.SUM(Allocation.primary_12)
            + fn.SUM(Allocation.primary_15)
            + fn.SUM(Allocation.primary_20)
            + fn.SUM(Allocation.secondary_5)
            + fn.SUM(Allocation.secondary_10)
        )
        .where(
            Allocation.department == department,
            Allocation.termCode == termCode,
        )
        .scalar()
    )
    result["allocated"] = totalPositions or 0

    usedAllocation = (
        LaborStatusForm.select()
        .join(FormHistory, on=(FormHistory.formID == LaborStatusForm.laborStatusFormID))
        .where(
            LaborStatusForm.department == department,
            LaborStatusForm.termCode == termCode,
            LaborStatusForm.contractHours.is_null(True),
            FormHistory.historyType == "Labor Status Form",
            ~(FormHistory.status % "Denied%"),
        )
        .count()
    )
    result["used"] = usedAllocation

    result["usedPositions"] = {
        "used10": countWorkers(department, termCode, "Primary", 10),
        "used12": countWorkers(department, termCode, "Primary", 12),
        "used15": countWorkers(department, termCode, "Primary", 15),
        "used20": countWorkers(department, termCode, "Primary", 20),
        "usedSecondary5": countWorkers(department, termCode, "Secondary", 5),
        "usedSecondary10": countWorkers(department, termCode, "Secondary", 10),
    }

    result["breakHours"] = getBreakHours(department, termCode)

    return result
