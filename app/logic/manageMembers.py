from datetime import date

from peewee import Case, fn

from app.models.formHistory import FormHistory
from app.models.laborReleaseForm import LaborReleaseForm
from app.models.laborStatusForm import LaborStatusForm
from app.models.term import Term


def getActivePendingPositionCounts(dept, currentYear):
    """Active/pending primary/secondary position counts for the selected academic year."""
    today = date.today()
    academicYearName = f"AY {currentYear[0]}-{currentYear[1]}"
    pendingStatuses = ["Pending", "Pre-Student Approval"]

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

    activePrimaries = ((LaborStatusForm.jobType == "Primary") & (FormHistory.status == "Approved"))
    pendingPrimaries = ((LaborStatusForm.jobType == "Primary") & (FormHistory.status.in_(pendingStatuses)))
    activeSecondaries = ((LaborStatusForm.jobType == "Secondary") & (FormHistory.status == "Approved"))
    pendingSecondaries = ((LaborStatusForm.jobType == "Secondary") & (FormHistory.status.in_(pendingStatuses)))

    rows = list(
        LaborStatusForm
        .select(
            LaborStatusForm.department,
            LaborStatusForm.supervisor,
            fn.SUM(Case(None, ((activePrimaries, 1),), 0)).alias("active_primary_positions"),
            fn.SUM(Case(None, ((pendingPrimaries, 1),), 0)).alias("pending_primary_positions"),
            fn.SUM(Case(None, ((activeSecondaries, 1),), 0)).alias("active_secondary_positions"),
            fn.SUM(Case(None, ((pendingSecondaries, 1),), 0)).alias("pending_secondary_positions"),
        )
        .join(Term, on=(LaborStatusForm.termCode == Term.termCode))
        .switch(LaborStatusForm)
        .join(FormHistory, on=(FormHistory.formID == LaborStatusForm.laborStatusFormID))
        .where(
            (LaborStatusForm.department == dept) &
            (Term.termName == academicYearName) &
            (FormHistory.historyType == "Labor Status Form") &
            (FormHistory.status.in_(["Approved"] + pendingStatuses)) &
            (LaborStatusForm.laborStatusFormID.not_in(releasedFormIds))
        )
        .group_by(LaborStatusForm.department, LaborStatusForm.supervisor).dicts()
    )

    return {
        (row["department"], row["supervisor"]): row
        for row in rows
    }

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