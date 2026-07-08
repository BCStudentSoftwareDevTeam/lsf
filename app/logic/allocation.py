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


def getAllocationSummary(dept, term):
    """
    Returns a dict describing a department's allocation vs. actual usage for the given term:
      - allocation: the Allocation row for this dept/term, or None if none exists
      - allocationBands: {fieldName: {'used': int, 'allocated': int}} per hour-band, or None
      - totalPositionsAllocated / totalPositionsUsed: ints, or None
      - breakHoursUsed: int, or None
    'used' counts are non-denied LaborStatusForms, matching the same filter pattern
    used elsewhere in the app (see app/logic/statusFormFunctions.py).
    """
    summary = {
        'allocation': None,
        'allocationBands': None,
        'totalPositionsAllocated': None,
        'totalPositionsUsed': None,
        'breakHoursUsed': None,
    }

    if not (dept and term):
        return summary

    allocation = Allocation.get_or_none(Allocation.department == dept, Allocation.termCode == term)
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


def getAllocationWarning(dept, term):
    """
    Returns a summary dict for displaying an over-allocation warning for the given
    department/term (e.g. in the pending-LSF approval modal), or None if there's no
    allocation on record for that department/term to compare against.

    Note: 'used' counts (from getAllocationSummary) include Pending as well as
    Approved forms, so a form currently Pending already occupies a slot here -
    these numbers already reflect what utilization would be once it's approved.
    """
    summary = getAllocationSummary(dept, term)
    if not summary['allocation']:
        return None

    positionsRemaining = summary['totalPositionsAllocated'] - summary['totalPositionsUsed']
    breakHoursRemaining = summary['allocation'].breakHours - summary['breakHoursUsed']
    isPositionsOverAllocated = positionsRemaining < 0
    isBreakHoursOverAllocated = breakHoursRemaining < 0

    return {
        'departmentName': dept.DEPT_NAME,
        'totalPositionsAllocated': summary['totalPositionsAllocated'],
        'totalPositionsUsed': summary['totalPositionsUsed'],
        'positionsRemaining': positionsRemaining,
        'isPositionsOverAllocated': isPositionsOverAllocated,
        'breakHoursAllocated': summary['allocation'].breakHours,
        'breakHoursUsed': summary['breakHoursUsed'],
        'breakHoursRemaining': breakHoursRemaining,
        'isBreakHoursOverAllocated': isBreakHoursOverAllocated,
        'isOverAllocated': isPositionsOverAllocated or isBreakHoursOverAllocated,
    }
