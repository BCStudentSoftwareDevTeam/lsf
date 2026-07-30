from app.models.supervisor import Supervisor
from app.models.supervisorDepartment import SupervisorDepartment
from peewee import fn
from app.logic.search import usernameFromEmail



def buildSupervisorDisplay(supervisor):
    """Build supervisor data used by portal displays and search results."""
    firstName = (supervisor.FIRST_NAME or "").strip()
    lastName = (supervisor.LAST_NAME or "").strip()
    email = (supervisor.EMAIL or "").strip()

    if not firstName or not lastName:
        return None

    return {
        "name": f"{firstName} {lastName}",
        "email": email,
        "username": usernameFromEmail(email) if email else "",
        "firstName": firstName,
        "lastName": lastName,
        "bnumber": supervisor.ID.strip(),
        "department": (supervisor.DEPT_NAME or "").strip(),
        "type": "Supervisor"
    }
def getSupervisorDepartments(dept):
    """Return supervisor-department records for a department."""
    if dept is None:
        return []

    return list(
        SupervisorDepartment
        .select(SupervisorDepartment, Supervisor)
        .join(Supervisor)
        .where(SupervisorDepartment.department == dept)
        .order_by(Supervisor.LAST_NAME.asc())
    )
def getSupervisors(dept):
    laborCoordinators = []
    supervisors = []

    for supervisorDepartment in getSupervisorDepartments(dept):
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