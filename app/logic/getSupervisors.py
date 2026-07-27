from app.models.supervisor import Supervisor
from app.models.supervisorDepartment import SupervisorDepartment
from peewee import fn



def buildSupervisorDisplay(supervisor):
    try:
        firstName = supervisor.FIRST_NAME 
        lastName = supervisor.LAST_NAME
        if not (firstName and lastName):
            raise NameError("First name and last name are required")

    except NameError as e:
        return None

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
            .order_by(Supervisor.LAST_NAME.asc()))
        for supervisorDepartment in supervisorDepartments:
            supervisor = supervisorDepartment.supervisor
            if supervisor is None:
                continue

            supervisorDisplay = buildSupervisorDisplay(supervisor)
            if not supervisorDisplay:
                continue

            if supervisorDepartment.isCoordinator:
                laborCoordinators.append(supervisorDisplay)
            else:
                supervisors.append(supervisorDisplay)

    return supervisors, laborCoordinators