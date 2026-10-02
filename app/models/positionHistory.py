from app.models import *
from app.models.department import Department

class PositionHistory(baseModel):
    positionCode       = CharField()
    department         = ForeignKeyField(Department)
    status             = CharField()
    wls                = IntegerField()
    revisionDate       = DateField()
    description        = TextField(default=None)

    class Meta:
        indexes = ( (('positionCode', 'revisionDate', 'status'), True), )
