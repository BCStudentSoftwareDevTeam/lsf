from datetime import datetime

from flask import g, render_template, request, send_file
from peewee import DoesNotExist

from app.controllers.main_routes import main_bp
from app.logic.download import makePositionDescriptionPDF
from app.logic.getPositions import getPosition, getPositions, getPositionDescriptionSections
from app.models.department import Department
from app.models.positionHistory import PositionHistory
from app.models.supervisorDepartment import SupervisorDepartment

@main_bp.route('/department/<org>/<account>/positions/<positionCode>', methods=['GET'])
def postionDescription(org, account, positionCode):
    try:
        dept = Department.get(Department.ORG == org, Department.ACCOUNT == account)
    except (NameError, DoesNotExist):
        return render_template('errors/404.html'), 404

    revisionDateParam = request.args.get('revisionDate')
    revisionDate = None
    if revisionDateParam:
        try:
            revisionDate = datetime.strptime(revisionDateParam, '%Y-%m-%d').date()
        except ValueError:
            return render_template('errors/404.html'), 404

    position = getPosition(dept, positionCode, revisionDate)

    if not position:
        return render_template('errors/404.html'), 404

    sections = getPositionDescriptionSections(position)

    return render_template(
        'main/individualPositions.html',
        department=dept,
        position=position,
        sections=sections
    )


@main_bp.route('/department/<org>/<account>/positions/<positionCode>/download', methods=['GET'])
def downloadPositionDescription(org, account, positionCode):
    try:
        dept = Department.get(Department.ORG == org, Department.ACCOUNT == account)
    except (NameError, DoesNotExist):
        return render_template('errors/404.html'), 404

    revisionDateParam = request.args.get('revisionDate')
    revisionDate = None
    if revisionDateParam:
        try:
            revisionDate = datetime.strptime(revisionDateParam, '%Y-%m-%d').date()
        except ValueError:
            return render_template('errors/404.html'), 404

    position = getPosition(dept, positionCode, revisionDate)

    if not position:
        return render_template('errors/404.html'), 404

    pdfBuffer = makePositionDescriptionPDF(dept, position)

    filename = f'{position.positionCode}_position_description.pdf'
    return send_file(pdfBuffer, mimetype='application/pdf', as_attachment=True, download_name=filename)



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

    positions = getPositions(dept)

    return render_template('main/managePositions.html',
                           department = dept,
                           department_name = dept.DEPT_NAME,
                           positions = positions
                           )
