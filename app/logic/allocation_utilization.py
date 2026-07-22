from peewee import fn

from app.models.allocation import Allocation
from app.models.laborStatusForm import LaborStatusForm


def get_department_allocation_summary(department, term_code):
    """Return allocation-utilization values for one department and term."""
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

    used_allocation = (
        LaborStatusForm.select()
        .where(
            LaborStatusForm.department == department,
            LaborStatusForm.termCode == term_code,
            LaborStatusForm.contractHours.is_null(True),
        )
        .count()
    )

    def count_workers(job_type, hours_bucket):
        return (
            LaborStatusForm.select()
            .where(
                LaborStatusForm.department == department,
                LaborStatusForm.termCode == term_code,
                LaborStatusForm.jobType == job_type,
                LaborStatusForm.weeklyHours == hours_bucket,
                LaborStatusForm.contractHours.is_null(True),
            )
            .count()
        )

    used_positions = {
        "used_10": count_workers("Primary", 10),
        "used_12": count_workers("Primary", 12),
        "used_15": count_workers("Primary", 15),
        "used_20": count_workers("Primary", 20),
        "used_5_sec": count_workers("Secondary", 5),
        "used_10_sec": count_workers("Secondary", 10),
    }

    break_hours = sum(
        form.contractHours or 0
        for form in LaborStatusForm.select(LaborStatusForm.contractHours).where(
            LaborStatusForm.department == department,
            LaborStatusForm.termCode == term_code,
            LaborStatusForm.contractHours.is_null(False),
        )
    )

    return {
        "total_positions": total_positions or 0,
        "used_allocation": used_allocation,
        "used_positions": used_positions,
        "break_hours": break_hours,
    }
