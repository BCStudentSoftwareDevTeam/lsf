from flask import abort
from flask_restful import Resource

from app.models.department import Department
from app.models.student import Student
from app.logic.apiEndpoint import getLaborInformation

class LaborFormsForDepartmentApi(Resource):
    def get(self, orgCode): 
        if Department.select().where(Department.ORG == orgCode).exists():
            dptForms = getLaborInformation(orgCode = orgCode)
            return dptForms
        else:
            abort(404)

class LaborFormsForStudentApi(Resource):
    def get(self, bNumber):
        if Student.select().where(Student.ID == bNumber).exists():
            stuForms = getLaborInformation(bNumber = bNumber)
            return stuForms
        else:
            abort(404)
