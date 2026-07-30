from flask import render_template, g
from app.controllers.main_routes import main_bp
from app.logic.getPositions import supervisorsPositions
from peewee import DoesNotExist
from app.models.department import Department
from app.models.supervisorDepartment import SupervisorDepartment

@main_bp.route('/department/<org>/<account>/positions', methods=['GET'])
def managePositions(org, account):
    try:
        dept = Department.get(Department.ORG == org, Department.ACCOUNT == account)
    except DoesNotExist:
        return render_template('errors/404.html'), 404
    
    if not g.currentUser.isLaborAdmin:
        if not SupervisorDepartment.select().where(
            (SupervisorDepartment.supervisor == g.currentUser.supervisor) &
            (SupervisorDepartment.department == dept.departmentID)
        ).exists():
            return render_template('errors/403.html'), 403

    positions = supervisorsPositions(dept)

    return render_template('main/managePositions.html',
                           department = dept,
                           department_name = dept.DEPT_NAME,
                           positions = positions
                           )
