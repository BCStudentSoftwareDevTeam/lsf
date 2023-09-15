from flask import abort
from app.models.department import Department
from app.models.student import Student

from app.controllers.api_routes import api_bp
from app.logic.apiEndpoint import getFormsForOrg, getFormsForStudent

@api_bp.route('/api/org/<orgCode>', methods=['GET'])
def getLaborForms(orgCode):
    # TODO: Need to add authentication
    if Department.select().where(Department.ORG == orgCode).exists():
        return getFormsForOrg(orgCode)
    else: 
        abort(404)

@api_bp.route('/api/usr/<bNumber>', methods=['GET'])
def getUserLaborForm(bNumber):
    if Student.select().where(Student.ID == bNumber).exists():
        return getFormsForStudent(bNumber)
    else:
        abort(404)