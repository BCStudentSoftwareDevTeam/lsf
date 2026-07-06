from app.models import *
from app.models.department import Department

class PositionHistory(baseModel):
    positioncode       = PrimaryKeyField()
    status             = CharField()
    WLS                = IntegerField()
    revisiondate       = DateField()
    Description        = TextField()
    Department         = ForeignKeyField(Department)               
