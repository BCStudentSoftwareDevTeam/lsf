from app.models import *
from app.models.department import Department

class PositionHistory(baseModel):
    positionTitle      = CharField()
    positionCode       = CharField()
    department         = ForeignKeyField(Department)
    status             = CharField()
    WLS                = IntegerField()
    revisiondate       = DateField()
    Description        = TextField(default=None)
    Department         = ForeignKeyField(Department)

    class Meta:
        primary_key = CompositeKey('positioncode', 'revisiondate', 'status')