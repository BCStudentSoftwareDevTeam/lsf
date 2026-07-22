from app.models import *
from app.models.department import Department

class PositionHistory(baseModel):
    positionTitle      = CharField()
    positionCode       = CharField()
    department         = ForeignKeyField(Department)
    status             = CharField()
    wls                = IntegerField()
    revisionDate       = DateField()
    description        = TextField(default=None)

    class Meta:
        indexes = ( (('positionCode', 'revisionDate', 'status'), False), )

