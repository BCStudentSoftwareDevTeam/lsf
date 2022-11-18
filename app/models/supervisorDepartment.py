from app.models import *
from app.models.supervisor import Supervisor
from app.models.department import Department
from peewee import CharField

class SupervisorDepartment(baseModel):
        supervisor          = ForeignKeyField(Supervisor)
        department          = ForeignKeyField(Department)
