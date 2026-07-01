from app.models import *
from app.models.department import Department

class PositionHistory(baseModel):
    positionID         = PrimaryKeyField()
    positioncode       = CharField()
    status             = CharField()
    WLS                = IntegerField()
    revisiondate       = DateField()
    Description        = TextField(default=None)
    Department         = ForeignKeyField(Department)               
