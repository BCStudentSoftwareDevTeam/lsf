from app.models import *
from app.models.department import Department
from app.models.supervisor import Supervisor
from app.models.term import Term

class Allocation(baseModel):
    termCode       = ForeignKeyField(Term)
    department     = ForeignKeyField(Department)
    isFinal        = BooleanField(default=False)
    approvedOn     = DateField(null=True)
    approvedBy     = ForeignKeyField(Supervisor, null=True)
    justification  = TextField(default="", null=False)
    primary_10     = IntegerField()
    primary_12     = IntegerField()
    primary_15     = IntegerField()
    primary_20     = IntegerField()
    secondary_5    = IntegerField()
    secondary_10   = IntegerField()
    breakHours     = IntegerField()

    class Meta:
        indexes = ( (('termCode', 'department', 'isFinal'), True), )

