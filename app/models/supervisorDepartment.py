from app.models import *
from app.models.supervisor import Supervisor
from app.models.department import Department

class SupervisorDepartment(baseModel):
    supervisor = ForeignKeyField(Supervisor)
    department = ForeignKeyField(Department)
    isActive = BooleanField(default=False)
    isCoordinator = BooleanField(default=False)


