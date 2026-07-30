from datetime import datetime
from flask import render_template, send_file, request
from peewee import DoesNotExist

from app.models.department import Department
from app.models.positionHistory import PositionHistory

from app.controllers.main_routes import main_bp
from app.logic.download import makePositionDescriptionPDF
from app.logic.getPositions import getPosition

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

    return render_template(
        'main/individualPositions.html',
        department=dept,
        position=position
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