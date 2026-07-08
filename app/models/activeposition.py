from app.models import *
from app.models.department import Department

class Activeposition(baseModel):
    title             = CharField()
    positioncode       = CharField()
    status             = CharField(default="Approved")
    WLS                = IntegerField()
    revisiondate       = DateField()
    Description        = TextField(default=None)
    Department         = ForeignKeyField(Department)
    
