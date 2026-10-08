from app.models import *
from app.models.department import Department

class PositionHistory(baseModel):
    positionTitle      = CharField()
    positionCode       = CharField()
    department         = ForeignKeyField(Department)
    status             = CharField() # Active, Inactive, Requested
    wls                = IntegerField()
    revisionDate       = DateField()
    revisedBy          = CharField()

    class Meta:
        indexes = ( (('positionCode', 'revisionDate', 'status'), True), )

