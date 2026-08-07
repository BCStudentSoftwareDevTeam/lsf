from app.models import *
from app.models.department import Department
from app.models.term import Term
from app.models.user import User


class PositionReview(baseModel):
    academicYear   = ForeignKeyField(Term)
    department     = ForeignKeyField(Department)
    requestedOn    = DateTimeField()
    requestedBy    = ForeignKeyField(User)

    class Meta:
        indexes = ( (('academicYear', 'department'), True), )
