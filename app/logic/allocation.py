from peewee import fn

from app.models.allocation import Allocation
from app.models.laborStatusForm import LaborStatusForm
from app.models.formHistory import FormHistory
from app.models.term import Term

# (Allocation field name, LaborStatusForm.jobType, LaborStatusForm.weeklyHours)
ALLOCATION_BAND_FIELDS = [
    ('primary_10', 'Primary', 10),
    ('primary_12', 'Primary', 12),
    ('primary_15', 'Primary', 15),
    ('primary_20', 'Primary', 20),
    ('secondary_5', 'Secondary', 5),
    ('secondary_10', 'Secondary', 10),
]

BAND_LABELS = {fieldName: f"{hours} Hour {jobType}" for fieldName, jobType, hours in ALLOCATION_BAND_FIELDS}


def getTotalAllocations(term, dept):
    """Return the department's allocated totals per band for a term."""
    if not term or not dept:
        return None

    allocation = Allocation.get_or_none(Allocation.department == dept, Allocation.termCode == term)
    if not allocation:
        return None

    bandTotals = {fieldName: getattr(allocation, fieldName) for fieldName, _, _ in ALLOCATION_BAND_FIELDS}
    return {
        "allocation": allocation,
        "bandTotals": bandTotals,
        "totalAllocations": sum(bandTotals.values()),
    }


def getContractedAllocations(term, dept):
    """Return the department's used positions per band and approved break hours for a term."""
    if not term or not dept:
        return None

    usedPositions = {}
    for fieldName, jobType, hours in ALLOCATION_BAND_FIELDS:
        usedPositions[fieldName] = (
            LaborStatusForm.select()
            .join(FormHistory, on=(FormHistory.formID == LaborStatusForm.laborStatusFormID))
            .where(
                LaborStatusForm.department == dept,
                LaborStatusForm.termCode == term,
                LaborStatusForm.jobType == jobType,
                LaborStatusForm.weeklyHours == hours,
                FormHistory.historyType == "Labor Status Form",
                ~(FormHistory.status % "Denied%"),
            )
            .distinct()
            .count()
        )

    # Break hours are tracked on separate break-term rows (e.g. Thanksgiving Break)
    # that share the same academic year prefix as the given AY term.
    yearPrefix = str(term.termCode)[:-2]
    breakTermCodes = [
        t.termCode for t in Term.select().where(Term.isBreak == True)
        if str(t.termCode).startswith(yearPrefix)
    ]
    breakHours = (
        LaborStatusForm.select(fn.SUM(LaborStatusForm.contractHours))
        .join(FormHistory, on=(FormHistory.formID == LaborStatusForm.laborStatusFormID))
        .where(
            LaborStatusForm.department == dept,
            LaborStatusForm.termCode.in_(breakTermCodes),
            FormHistory.historyType == "Labor Status Form",
            ~(FormHistory.status % "Denied%"),
        )
        .scalar()
    ) or 0

    return {
        "usedPositions": usedPositions,
        "usedTotal": sum(usedPositions.values()),
        "breakHours": breakHours,
    }


def getBandAllocationStatus(dept, term, jobType, hours):
    fieldName = next((f for f, j, h in ALLOCATION_BAND_FIELDS if j == jobType and h == hours), None)
    if not fieldName:
        return None

    totals = getTotalAllocations(term, dept)
    if not totals:
        return None
    contracted = getContractedAllocations(term, dept)

    allocated = totals["bandTotals"][fieldName]
    used = contracted["usedPositions"][fieldName]
    return {
        'label': BAND_LABELS[fieldName],
        'used': used,
        'allocated': allocated,
        'remaining': allocated - used,
        'isOverAllocated': used > allocated,
    }


def getAllocationWarning(dept, term):
    totals = getTotalAllocations(term, dept)
    if not totals:
        return None
    contracted = getContractedAllocations(term, dept)

    positionsRemaining = totals["totalAllocations"] - contracted["usedTotal"]
    breakHoursRemaining = totals["allocation"].breakHours - contracted["breakHours"]

    # A department can be within its total position count while still exceeding
    # one specific hour-band (e.g. over on 10-hour Primary but under on others),
    # so each band needs to be checked individually, not just the aggregate total.
    overAllocatedBands = [
        {'label': BAND_LABELS[fieldName], 'used': contracted["usedPositions"][fieldName], 'allocated': totals["bandTotals"][fieldName]}
        for fieldName, _, _ in ALLOCATION_BAND_FIELDS
        if contracted["usedPositions"][fieldName] > totals["bandTotals"][fieldName]
    ]
    isPositionsOverAllocated = positionsRemaining < 0 or bool(overAllocatedBands)
    isBreakHoursOverAllocated = breakHoursRemaining < 0

    return {
        'departmentName': dept.DEPT_NAME,
        'totalPositionsAllocated': totals["totalAllocations"],
        'totalPositionsUsed': contracted["usedTotal"],
        'positionsRemaining': positionsRemaining,
        'isPositionsOverAllocated': isPositionsOverAllocated,
        'overAllocatedBands': overAllocatedBands,
        'breakHoursAllocated': totals["allocation"].breakHours,
        'breakHoursUsed': contracted["breakHours"],
        'breakHoursRemaining': breakHoursRemaining,
        'isBreakHoursOverAllocated': isBreakHoursOverAllocated,
        'isOverAllocated': isPositionsOverAllocated or isBreakHoursOverAllocated,
    }
