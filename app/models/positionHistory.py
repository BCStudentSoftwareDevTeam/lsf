from app.models import *
from app.models.department import Department

class PositionHistory(baseModel):
    positionTitle      = CharField(null=True)
    positionCode       = CharField(null=True)
    department         = ForeignKeyField(Department)
    status             = CharField(null=True)
    wls                = IntegerField(null=True)
    revisionDate       = DateField(null=True)
    revisedBy          = CharField(null=True)
    description        = TextField(default=None)
    # True once an Annual Position Review request has gone out for this position.
    # Nothing resets it yet, so a position is only ever requested once - the Labor
    # Office's review workflow isn't defined. Possible later additions: a reset
    # function (per department or all) for the Labor Office to trigger, or an
    # automatic reset when a new academic year starts.
    reviewRequested    = BooleanField(default=False)

    class Meta:
        indexes = ( (('positionCode', 'revisionDate', 'status'), True), )

