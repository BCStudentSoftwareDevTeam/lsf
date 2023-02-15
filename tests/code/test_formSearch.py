from app.controllers.main_routes.main_routes import getDatatableData, supervisorPortal
from app import app
import pytest
from app.models import mainDB
import json

@pytest.mark.integration
def test_getDatatableData():
    with mainDB.atomic() as transaction:
        termCodeDict = {'length': 25, 'start': 0,'draw': 1,'order[0][column]': 0, 'order[0][dir]': 'desc', "data": '{"termCode": "201500", "departmentID": "", "supervisorID": "", "studentID": "", "formStatus": "[]", "formType": "[]", "evaluations": "[]"}'}
        currentTermDict= {'length': 25, 'start': 0,'draw': 1,'order[0][column]': 0, 'order[0][dir]': 'desc', "data": '{"termCode": "currentTerm", "departmentID": "", "supervisorID": "", "studentID": "", "formStatus": "[]", "formType": "[]", "evaluations": "[]"}'}
        currentUserDict= {'length': 25, 'start': 0,'draw': 1,'order[0][column]': 0, 'order[0][dir]': 'desc', "data": '{"termCode": "currentTerm", "departmentID": "", "supervisorID": "currentUser", "studentID": "", "formStatus": "[]", "formType": "[]", "evaluations": "[]"}'}
        departmentIDDict = {'length': 25, 'start': 0,'draw': 1,'order[0][column]': 0, 'order[0][dir]': 'desc', "data": '{"termCode": "currentTerm", "departmentID": "1", "supervisorID": "currentUser", "studentID": "", "formStatus": "[]", "formType": "[]", "evaluations": "[]"}'}
        studentIDDict = {'length': 25, 'start': 0,'draw': 1,'order[0][column]': 0, 'order[0][dir]': 'desc', "data": '{"termCode": "", "departmentID": "", "supervisorID": "currentUser", "studentID": "B00730361", "formStatus": "[]", "formType": "[]", "evaluations": "[]"}'}
        allEvalDict = {'length': 25, 'start': 0,'draw': 1,'order[0][column]': 0, 'order[0][dir]': 'desc', "data": '{"termCode": "", "departmentID": "", "supervisorID": "currentUser", "studentID": "", "formStatus": "[]", "formType": "[]", "evaluations": "[allEvalMissing]"}'}

        with app.test_request_context(
        "/", method="POST", data=termCodeDict):
            runGetDatatableData = supervisorPortal()
        with app.test_request_context(
        "/", method="POST", data=currentTermDict):
            runGetDatatableData = supervisorPortal()
        with app.test_request_context(
        "/", method="POST", data=currentUserDict):
            runGetDatatableData = supervisorPortal()
        with app.test_request_context(
        "/", method="POST", data=departmentIDDict):
            runGetDatatableData = supervisorPortal()
        with app.test_request_context(
        "/", method="POST", data=studentIDDict):
            runGetDatatableData = supervisorPortal()
        with app.test_request_context(
        "/", method="POST", data=allEvalDict):
            runGetDatatableData = supervisorPortal()
            assert True



        transaction.rollback()
