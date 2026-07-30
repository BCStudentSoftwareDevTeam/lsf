from peewee import fn

from app.models.allocation import Allocation
from app.models.laborStatusForm import LaborStatusForm
from app.models.term import Term
from app.models.formHistory import FormHistory


def countWorkers(department, term_code, job_type, hours_bucket):
    workerCount = (
        LaborStatusForm.select()
        .join(FormHistory, on=(FormHistory.formID == LaborStatusForm.laborStatusFormID))
        .where(
            LaborStatusForm.department == department,
            LaborStatusForm.termCode == term_code,
            LaborStatusForm.jobType == job_type,
            LaborStatusForm.weeklyHours == hours_bucket,
            LaborStatusForm.contractHours.is_null(True),
            FormHistory.historyType == "Labor Status Form",
            ~(FormHistory.status % "Denied%"),
        )
        .count()
    )
    return workerCount


def getBreakHours(department, term_code):
    breakHoursTotal = (
        LaborStatusForm.select(fn.SUM(LaborStatusForm.contractHours))
        .join(FormHistory, on=(FormHistory.formID == LaborStatusForm.laborStatusFormID))
        .where(
            LaborStatusForm.department == department,
            LaborStatusForm.termCode == term_code,
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
        "allocated": 0,
        "used": 0,
        "used_positions": {
            "used_10": 0,
            "used_12": 0,
            "used_15": 0,
            "used_20": 0,
            "used_5_sec": 0,
            "used_10_sec": 0,
        },
        "break_hours": 0,
    }

    departmentAllocations = list(
        Allocation.select(Allocation, Term).join(Term).where(Allocation.department == department)
    )
    if not departmentAllocations:
        return result

    recentTerm = Term.order_by_term([a.termCode for a in departmentAllocations], reverse=True)[0]
    term_code = recentTerm.termCode
    result["term"] = recentTerm

    total_positions = (
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
            Allocation.termCode == term_code,
        )
        .scalar()
    )
    result["allocated"] = total_positions or 0

    used_allocation = (
        LaborStatusForm.select()
        .join(FormHistory, on=(FormHistory.formID == LaborStatusForm.laborStatusFormID))
        .where(
            LaborStatusForm.department == department,
            LaborStatusForm.termCode == term_code,
            LaborStatusForm.contractHours.is_null(True),
            FormHistory.historyType == "Labor Status Form",
            ~(FormHistory.status % "Denied%"),
        )
        .count()
    )
    result["used"] = used_allocation

    result["used_positions"] = {
        "used_10": countWorkers(department, term_code, "Primary", 10),
        "used_12": countWorkers(department, term_code, "Primary", 12),
        "used_15": countWorkers(department, term_code, "Primary", 15),
        "used_20": countWorkers(department, term_code, "Primary", 20),
        "used_5_sec": countWorkers(department, term_code, "Secondary", 5),
        "used_10_sec": countWorkers(department, term_code, "Secondary", 10),
    }

    result["break_hours"] = getBreakHours(department, term_code)

    return result
