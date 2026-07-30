from flask import render_template, send_file
from peewee import DoesNotExist

from app.models.department import Department
from app.models.positionHistory import PositionHistory

from app.controllers.main_routes import main_bp
from app.logic.download import makePositionDescriptionPDF


@main_bp.route('/department/<org>/<account>/positions/<positionCode>', methods=['GET'])
def postionDescription(org, account, positionCode):
    try:
        dept = Department.get(Department.ORG == org, Department.ACCOUNT == account)
    except (NameError, DoesNotExist):
        return render_template('errors/404.html'), 404

    position = PositionHistory.get_or_none(
        PositionHistory.department == dept,
        PositionHistory.positionCode == positionCode,
        PositionHistory.status == "Active"
    )

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

    position = PositionHistory.get_or_none(
        PositionHistory.department == dept,
        PositionHistory.positionCode == positionCode,
        PositionHistory.status == "Active"
    )

    if not position:
        return render_template('errors/404.html'), 404

    pdfBuffer = makePositionDescriptionPDF(dept, position, position.revisedBy)

    filename = f'{position.positionCode}_position_description.pdf'
    return send_file(pdfBuffer, mimetype='application/pdf', as_attachment=True, download_name=filename)