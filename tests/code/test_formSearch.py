from app.controllers.main_routes.main_routes import getDatatableData, supervisorPortal
from app import app
import pytest
from app.models import mainDB
import json

@pytest.mark.integration
def test_getDatatableData():
    with mainDB.atomic() as transaction:
        dict = {'length': 25, 'start': 0,'draw': 1,'order[0][column]': 0, 'order[0][dir]': 'desc', "data": '{"termCode": "201500", "departmentID": "", "supervisorID": "", "studentID": "", "formStatus": "[]", "formType": "[]", "evaluations": "[]"}'}
        with app.test_request_context(
        "/", method="POST", data=dict):
            runGetDatatableData = supervisorPortal()
            print(runGetDatatableData)
            assert True

        transaction.rollback()
