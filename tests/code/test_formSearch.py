from app.controllers.main_routes.main_routes import getDatatableData, supervisorPortal
from app import app
from flask import g
import pytest
from app.models import mainDB
from app.models.user import User
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
        with app.test_request_context("/", method="POST", data=termCodeDict):
            runGetDatatableData = supervisorPortal()
        
        with app.test_request_context("/", method="POST", data=currentTermDict):
            g.openTerm = 201500
            runGetDatatableData = supervisorPortal()
            
        with app.test_request_context("/", method="POST", data=currentUserDict):
            g.openTerm = 201500
            g.currentUser = User.get_by_id(1)         
            runGetDatatableData = supervisorPortal()
            
        with app.test_request_context("/", method="POST", data=departmentIDDict):
            g.openTerm = 201500
            g.currentUser = User.get_by_id(1) 
            runGetDatatableData = supervisorPortal()
            
        with app.test_request_context("/", method="POST", data=studentIDDict):
            g.currentUser = User.get_by_id(1) 
            runGetDatatableData = supervisorPortal()
        
        with app.test_request_context("/", method="POST", data=allEvalDict):
            g.currentUser = User.get_by_id(1) 
            runGetDatatableData = supervisorPortal()
            
            assert True



        transaction.rollback()
