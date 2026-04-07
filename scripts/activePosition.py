from app.models.activePosition import *
from app.models.laborStatusForm import *
from app.models.department import * 
from app.models import mainDB

def populate_active_positions():
    created = duplicates = skipped = 0
    seen = set()
    positions = (
        LaborStatusForm
        .select()
        .where(
            (LaborStatusForm.POSN_CODE.is_null(False)) &
            (LaborStatusForm.POSN_CODE != "")
        )
    )
    with mainDB.atomic():
        for row in positions:
            if not row.department:
                skipped += 1
                continue

            key = (row.department.id, row.POSN_CODE)
            if key in seen:
                duplicates += 1
                continue
            seen.add(key)

            existing = ActivePosition.get_or_none((ActivePosition.department == row.department) & (ActivePosition.POSN_CODE == row.POSN_CODE))
            if not existing:
                ActivePosition.create( department=row.department, POSN_TITLE=row.POSN_TITLE, POSN_CODE=row.POSN_CODE, WLS=row.WLS )
                created += 1
    print(f"Created: {created}; Duplicates ignored: {duplicates}; Skipped: {skipped}")

if __name__ == "__main__":
    populate_active_positions()