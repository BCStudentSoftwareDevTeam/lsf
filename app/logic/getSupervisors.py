from app.logic.search import usernameFromEmail
from app.models.supervisor import Supervisor
from app.models.supervisorDepartment import SupervisorDepartment


def buildSupervisorDisplay(supervisor):
    """Build supervisor data used by portal displays and search results."""
    firstName = (
        supervisor.preferred_name or
        supervisor.legal_name or
        ""
    ).strip()
    lastName = (supervisor.LAST_NAME or "").strip()
    email = supervisor.EMAIL.strip() if supervisor.EMAIL else None

    if not firstName or not lastName:
        return None

    return {
        "name": f"{firstName} {lastName}",
        "email": email,
        "username": usernameFromEmail(email) if email else None,
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