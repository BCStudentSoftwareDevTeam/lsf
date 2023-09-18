from flask import abort, request
from flask_restful import Resource

from app import app
from app.config.loadConfig import get_secret_cfg

from app.models.department import Department
from app.models.student import Student
from app.logic.apiEndpoint import getLaborInformation

class LaborFormsForDepartmentApi(Resource):
    def get(self, orgCode): 
        appConfig = get_secret_cfg()
        requestersIp = request.remote_addr

        if app.config['ENV'] == 'production' and not requestersIp == appConfig['VALID_REQUEST_IP']:
            abort(403)

        if Department.select().where(Department.ORG == orgCode).exists():
            dptForms = getLaborInformation(orgCode = orgCode)
            return dptForms
        else:
            abort(404)

class LaborFormsForStudentApi(Resource):
    def get(self, bNumber):
        appConfig = get_secret_cfg()
        requestersIp = request.remote_addr

        if app.config['ENV'] == 'production' and not requestersIp == appConfig['VALID_REQUEST_IP']:
            abort(403)

        if Student.select().where(Student.ID == bNumber).exists():
            stuForms = getLaborInformation(bNumber = bNumber)
            return stuForms
        else:
            abort(404)