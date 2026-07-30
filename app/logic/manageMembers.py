from datetime import date

from flask import abort
from peewee import Case, DoesNotExist, fn

from app.models.department import Department
from app.models.formHistory import FormHistory
from app.models.laborReleaseForm import LaborReleaseForm
from app.models.laborStatusForm import LaborStatusForm
from app.models.supervisor import Supervisor
from app.models.supervisorDepartment import SupervisorDepartment




def getStudentCounts(dept):
    """Active/pending primary/secondary position counts, keyed by (dept, supervisor)."""
    today = date.today()

    releasedFormIds = (
        FormHistory
        .select(FormHistory.formID)
        .join(LaborReleaseForm)
        .where(
            (FormHistory.historyType == "Labor Release Form") &
            (FormHistory.status == "Approved") &
            (LaborReleaseForm.releaseDate <= today)
        )
    )

    activePrimaries = (
        (LaborStatusForm.jobType == 'Primary') &
        (LaborStatusForm.studentConfirmation == True)
    )
    pendingPrimaries = (
        (LaborStatusForm.jobType == 'Primary') &
        (LaborStatusForm.studentConfirmation.is_null(True))
    )
    activeSecondaries = (
        (LaborStatusForm.jobType == 'Secondary') &
        (LaborStatusForm.studentConfirmation == True)
    )
    pendingSecondaries = (
        (LaborStatusForm.jobType == 'Secondary') &
        (LaborStatusForm.studentConfirmation.is_null(True))
    )

    rows = list(
        LaborStatusForm
        .select(
            fn.SUM(Case(None, ((activePrimaries, 1),), 0)).alias("active_primary_positions"),
            fn.SUM(Case(None, ((pendingPrimaries, 1),), 0)).alias("pending_primary_positions"),
            fn.SUM(Case(None, ((activeSecondaries, 1),), 0)).alias("active_secondary_positions"),
            fn.SUM(Case(None, ((pendingSecondaries, 1),), 0)).alias("pending_secondary_positions"),
            LaborStatusForm.department,
            LaborStatusForm.supervisor
        )
        .where(
            (LaborStatusForm.department == dept) &
            (LaborStatusForm.laborStatusFormID.not_in(releasedFormIds))
        )
        .group_by(LaborStatusForm.department, LaborStatusForm.supervisor)
        .dicts()
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