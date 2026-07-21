from app.models.supervisor import Supervisor
from app.models.supervisorDepartment import SupervisorDepartment
from peewee import fn



def buildSupervisorDisplay(supervisor):
    firstName = supervisor.preferred_name or supervisor.legal_name or ""
    lastName = supervisor.LAST_NAME or ""

    return {
        "name": f"{firstName} {lastName}".strip(),
        "email": supervisor.EMAIL
    }
def getSupervisors(dept):    
    laborCoordinators = []
    supervisors = []
    
    # Avoid querying department members unless the selected department exists.
    if dept is not None:
        supervisorDepartments = (SupervisorDepartment.select().join(Supervisor).where(SupervisorDepartment.department == dept)
            .order_by(fn.COALESCE(Supervisor.preferred_name, Supervisor.legal_name, Supervisor.LAST_NAME).asc()))
        

        for supervisorDepartment in supervisorDepartments:
            supervisor = supervisorDepartment.supervisor

            if supervisor is None:
                continue

            supervisorDisplay = buildSupervisorDisplay(supervisor)

            if supervisorDepartment.isCoordinator:
                laborCoordinators.append(supervisorDisplay)
            else:
                supervisors.append(supervisorDisplay)
    return supervisors, laborCoordinators