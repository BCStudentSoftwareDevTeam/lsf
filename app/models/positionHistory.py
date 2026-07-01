from app.models import *
from app.models.department import Department

class PositionHistory(baseModel):
    positioncode       = CharField()
    status             = CharField()
    WLS                = IntegerField()
    revisiondate       = DateField()
    Description        = TextField(default=None)
    Department         = ForeignKeyField(Department)
PositionHistory._meta.set_primary_key('positioncode_revisiondate_status', CompositeKey('positioncode', 'revisiondate', 'status'))          
