from datetime import date

from flask import abort
from peewee import Case, DoesNotExist, fn

from app.logic.search import usernameFromEmail
from app.models.department import Department
from app.models.formHistory import FormHistory
from app.models.laborReleaseForm import LaborReleaseForm
from app.models.laborStatusForm import LaborStatusForm
from app.models.supervisor import Supervisor
from app.models.supervisorDepartment import SupervisorDepartment

def supervisorsDbToDict(supervisor):
    """
    Given a supervisor object it will return a mapped Dict with supervisor data.
    """
    dbToDict =  {'username': usernameFromEmail(supervisor.EMAIL.strip()),
                'firstName': supervisor.FIRST_NAME.strip(),
                'lastName': supervisor.LAST_NAME.strip(),
                'bnumber': supervisor.ID.strip(),
                'department': supervisor.DEPT_NAME.strip(),
                'type': 'Supervisor'}
    return dbToDict

def currentAcademicYear():
    """
    Finds the current academic year
    """
    today = date.today()
    currentYear = today.year
    if today.month < 7: 
        currentAcademicYear = (currentYear - 1, currentYear)
    else: 
        currentAcademicYear = (currentYear, currentYear + 1)
    # Note that the start of July is 
    # normally considered the start of a new academic year.

    return currentAcademicYear

def getCurrentDepartment(org, account):
    """Look up the department by org/account, stash it in session, or 404."""
    try:
        return Department.get(
            Department.ORG == org,
            Department.ACCOUNT == account
        )
    except (NameError, DoesNotExist):
        abort(404)


def getDepartmentMembers(dept):
    """Supervisor-department rows for a department, as dicts."""
    return list(
        SupervisorDepartment.select(SupervisorDepartment, Supervisor)
        .join(Supervisor)
        .where(SupervisorDepartment.department == dept)
    )


def getReleasedFormIds():
    """formIDs for labor release forms already in effect as of today."""
    today = date.today()
    return (
        FormHistory.select(FormHistory.formID)
        .join(LaborReleaseForm)
        .where(
            (FormHistory.historyType == "Labor Release Form") &
            (FormHistory.status == "Approved") &
            (LaborReleaseForm.releaseDate <= today)
        )
    )


def getStudentCounts(dept):
    """Active/pending primary/secondary position counts, keyed by (dept, supervisor)."""
    releasedFormIds = getReleasedFormIds()

    activePrimaries = (LaborStatusForm.jobType == 'Primary') & (LaborStatusForm.studentConfirmation == True)
    pendingPrimaries = (LaborStatusForm.jobType == 'Primary') & (LaborStatusForm.studentConfirmation.is_null(True))
    activeSecondaries = (LaborStatusForm.jobType == 'Secondary') & (LaborStatusForm.studentConfirmation == True)
    pendingSecondaries = (LaborStatusForm.jobType == 'Secondary') & (LaborStatusForm.studentConfirmation.is_null(True))

    rows = list(
        LaborStatusForm.select(
            fn.SUM(Case(None, ((activePrimaries, 1),), 0)).alias("active_primary_positions"),
            fn.SUM(Case(None, ((pendingPrimaries, 1),), 0)).alias("pending_primary_positions"),
            fn.SUM(Case(None, ((activeSecondaries, 1),), 0)).alias("active_secondary_positions"),
            fn.SUM(Case(None, ((pendingSecondaries, 1),), 0)).alias("pending_secondary_positions"),
            LaborStatusForm.department,
            LaborStatusForm.supervisor
        ).where(
            (LaborStatusForm.department == dept) &
            (LaborStatusForm.laborStatusFormID.not_in(releasedFormIds))
        ).group_by(
            LaborStatusForm.department, LaborStatusForm.supervisor
        ).dicts()
    )
    return {(row["department"], row["supervisor"]): row for row in rows}


def attachPositionCounts(members, counts):
    """Attach position counts to each supervisor-department row."""
    fields = [
        "active_primary_positions",
        "pending_primary_positions",
        "active_secondary_positions",
        "pending_secondary_positions",
    ]

    for member in members:
        row = counts.get((member.department_id, member.supervisor_id), {})

        for field in fields:
            setattr(member, field, row.get(field, 0))

    return members

def canManageMembers(currentUser):
    """
    Returns True if the current user is allowed to manage department members.
    """
    return (
        getattr(currentUser, "isLaborAdmin", False) or
        getattr(currentUser, "isLaborDepartmentStudent", False)
    )
