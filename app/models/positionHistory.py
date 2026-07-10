from app.models import *
from app.models.department import Department

class PositionHistory(baseModel):
<<<<<<< HEAD
    positioncode       = PrimaryKeyField()
    status             = CharField()
    WLS                = IntegerField()
    revisiondate       = DateField()
    Description        = TextField()
    Department         = ForeignKeyField(Department)               
=======
    positionCode       = CharField()
    department         = ForeignKeyField(Department)
    status             = CharField()
    wls                = IntegerField()
    revisionDate       = DateField()
    description        = TextField(default=None)

    class Meta:
        indexes = ( (('positionCode', 'revisionDate', 'status'), True), )

>>>>>>> department-portal-base
