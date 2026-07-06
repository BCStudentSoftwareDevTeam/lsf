from app.models import *
from app.models.department import Department
from app.models.term import Term

class Allocation(baseModel):
    department      = ForeignKeyField(Department, on_delete="cascade")
    term            = ForeignKeyField(Term, on_delete="cascade")
    totalPositions  = IntegerField()
    totalBreakHours = IntegerField()
