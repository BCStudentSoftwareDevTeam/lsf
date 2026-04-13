from app.models import *
from app.models.department import Department

class ActivePosition(baseModel):
    department = ForeignKeyField(Department)
    POSN_TITLE = CharField()
    POSN_CODE = CharField()
    WLS = CharField(null=True)