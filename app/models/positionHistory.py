from app.models import *
from app.models.department import Department

class PositionHistory(baseModel):
    positioncode       = CharField()
    status             = CharField()
    WLS                = IntegerField()
    revisiondate       = DateField()
    Description        = TextField(default=None)
    Department         = ForeignKeyField(Department)

    class Meta:
        primary_key = CompositeKey('positioncode', 'revisiondate', 'status')