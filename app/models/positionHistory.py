from app.models import *
from app.models.department import Department
from app.models.term import Term
from app.models.user import User

class PositionHistory(baseModel):
    positionTitle      = CharField(null=True)
    positionCode       = CharField(null=True)
    department         = ForeignKeyField(Department)
    status             = CharField(null=True)
    wls                = IntegerField(null=True)
    revisionDate       = DateField(null=True)
    description        = TextField(default=None)
    academicYear       = ForeignKeyField(Term, null=True)
    requestedOn        = DateTimeField(null=True)
    requestedBy        = ForeignKeyField(User, null=True)

    class Meta:
        indexes = ( (('positionCode', 'revisionDate', 'status'), True), )

