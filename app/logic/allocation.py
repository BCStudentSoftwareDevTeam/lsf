from peewee import fn
from app.models.allocation import Allocation
from app.models.laborStatusForm import LaborStatusForm
from app.models.formHistory import FormHistory
from app.models.term import Term

# Each entry is (Allocation field name, LaborStatusForm.jobType, LaborStatusForm.weeklyHours)
ALLOCATION_BAND_FIELDS = [
    ('primary_10', 'Primary', 10),
    ('primary_12', 'Primary', 12),
    ('primary_15', 'Primary', 15),
    ('primary_20', 'Primary', 20),
    ('secondary_5', 'Secondary', 5),
    ('secondary_10', 'Secondary', 10),
]

BAND_LABELS = {fieldName: f"{hours} Hour {jobType}" for fieldName, jobType, hours in ALLOCATION_BAND_FIELDS}


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
        {'label': BAND_LABELS[fieldName], 'used': band['used'], 'allocated': band['allocated']}
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
