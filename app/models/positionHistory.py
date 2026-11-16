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
    # True once a Position Review request has gone out for this revision. A revision
    # gets a new row with this unset, so it can be requested again once that revision
    # is old enough (see getPositionsPendingReview).
    reviewRequested    = BooleanField(default=False)

    class Meta:
        indexes = ( (('positionCode', 'revisionDate', 'status'), True), )

