import pytest
from app import app
from app.controllers.main_routes.laborStatusForm import getPositions
from app.logic.statusFormFunctions import createOverloadForm
from app.models.user import User
from app.models.laborStatusForm import LaborStatusForm
from app.models.notes import Notes
from app.models.adjustedForm import AdjustedForm
from app.models.formHistory import FormHistory
from datetime import date, datetime
from app.logic.statusFormFunctions import createOverloadForm
from app.models import mainDB
from app.models.supervisor import Supervisor
from app.models.department import Department
from app.models.laborStatusForm import LaborStatusForm
from app.models.term import Term
from app.models.student import Student
from app.models.historyType import HistoryType
from app.models.status import Status
from flask import json, template_rendered
from contextlib import contextmanager

@pytest.fixture
def setup():
    delete_forms()

    yield

@pytest.fixture
def cleanup():
    yield
    delete_forms()


def delete_forms():
    formHistories = FormHistory.select().where((FormHistory.formID == 2) & (FormHistory.historyType == "Labor Adjustment Form"))
    FormHistory.delete().where((FormHistory.formID == 2) & (FormHistory.historyType == "Labor Overload Form")).execute()
    for form in formHistories:
        # form.delete().execute()
        AdjustedForm.delete().where(AdjustedForm.adjustedFormID == form.adjustedForm.adjustedFormID).execute()
    Notes.delete().where(Notes.formID.cast('char').contains("2")).execute()

def resetLSF():
    lsfInfo = {
    "supervisorNotes":"",
    "supervisor" : "B12361006",
    "position":"S61419",
    "weeklyHours":10,
    "contractHours": None
    }

    lsf.supervisorNotes = lsfInfo["supervisorNotes"]
    lsf.save()
    lsf.supervisor = lsfInfo["supervisor"]
    lsf.save()
    lsf.position = lsfInfo["position"]
    lsf.save()
    lsf.weeklyHours = lsfInfo["weeklyHours"]
    lsf.save()
    lsf.contractHours = lsfInfo["contractHours"]
    lsf.save()


currentUser = User.get(User.userID == 1) # Scott Heggen's entry in User table
lsf = LaborStatusForm.get(LaborStatusForm.laborStatusFormID == 2)
fieldsChanged = {'supervisor':{'oldValue':'B12361006', 'newValue':'B12365892','date':'07/21/2020'},
       'weeklyHours':{'oldValue': '10', 'newValue': '12', 'date': '07/21/2020'},
       'position':{'oldValue': 'S61419', 'newValue': 'S61407', 'date': '07/21/2020'},
       'supervisorNotes':{'oldValue':'old notes.', 'newValue':'new notes.'}
       }

fieldsChangedOverload = {'weeklyHours': {'oldValue':'10', 'newValue':'20', 'date': '07/21/2020'}}

fieldsChangedContractHours = {'contractHours':{'oldValue': '40', 'newValue': '60', 'date': '07/21/2020'}}

@pytest.mark.integration
def test_getPositions(setup):
    with mainDB.transaction() as transaction:
        deptOk = Department.create(DEPT_NAME="SSDT", ACCOUNT="SSDTACC", ORG="SSDTORG")
        deptOther = Department.create(DEPT_NAME="OTHER", ACCOUNT="OTHERACC", ORG="OTHERORG")
        term = Term.create(
            termCode=22332,
            termName="Fall 2020",
            termStart=date(2020, 7, 1),
            termEnd=date(2020, 12, 31),
            termState=True,
            adjustmentCutOff=date(2099, 1, 1),
        )
        student = Student.create(   
            ID="B12332123",
            preferred_name="Nyan",
            legal_name="Nyan",
            LAST_NAME="Zaw",
            STU_EMAIL="imran@berea.edu"
        )
        supervisor1 = Supervisor.create(ID="B12361007", PIDM = 14578, LAST_NAME = "Bledsoe", legal_name = "Finn", preferred_name = "Finn", EMAIL="bledsoef@berea.edu", CPO="5467", DEPT_Name="SSDT")
        supervisor2 = Supervisor.create(ID="B12365892", PIDM = 14579, LAST_NAME = "Bledsoe", legal_name = "Jason", preferred_name = "Jason", EMAIL="bledsoej@berea.edu", CPO="5468", DEPT_Name="SSDT")
        currentUser = User.get(User.userID == 3)
        status, _ = Status.get_or_create(statusName="Approved")
        historyType, _ = HistoryType.get_or_create(historyTypeName="Labor Status Form")
        lsfGood = LaborStatusForm.create(
            laborStatusFormID=98765,
            termCode=term,
            studentSupervisee=student,
            supervisor=supervisor1,
            department=deptOk,
            jobType="Primary",
            WLS="W1",
            POSN_TITLE="Good Position",
            POSN_CODE="S61407",
            contractHours=40,
            weeklyHours=10,
            supervisorNotes="old notes.",
        )
        lsfDummy = LaborStatusForm.create(
            laborStatusFormID=98766,
            termCode=term,
            studentSupervisee=student,
            supervisor=supervisor1,
            department=deptOk,
            jobType="Primary",
            WLS="WD",
            POSN_TITLE="Dummy Position",
            POSN_CODE="S12345",
            contractHours=40,
            weeklyHours=10,
            supervisorNotes="old notes.",
        )
        lsfOther = LaborStatusForm.create(
            laborStatusFormID=98767,
            termCode=term,
            studentSupervisee=student,
            supervisor=supervisor1,
            department=deptOther,
            jobType="Primary",
            WLS="WO",
            POSN_TITLE="Other Dept Position",
            POSN_CODE="S99999",
            contractHours=40,
            weeklyHours=10,
            supervisorNotes="old notes.",
        )
        FormHistory.create(
            formID=lsfGood,
            historyType=historyType,
            createdBy=currentUser,
            createdDate=date.today(),
            status=status,
        )
        FormHistory.create(
            formID=lsfDummy,
            historyType=historyType,
            createdBy=currentUser,
            createdDate=date.today(),
            status=status,
        )
        FormHistory.create(
            formID=lsfOther,
            historyType=historyType,
            createdBy=currentUser,
            createdDate=date.today(),
            status=status,
        )   
        with app.test_request_context():
            positions = json.loads(getPositions("SSDTORG", "SSDTACC"))
            assert "S12345" in positions
            assert "S61407" in positions

            assert positions["S12345"]["position"] == "Dummy Position"
            assert positions["S61407"]["position"] == "Good Position"
        resetLSF()
        transaction.rollback()
