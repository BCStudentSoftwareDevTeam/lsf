import pytest
from app import app
from app.controllers.main_routes.alterLSF import modifyLSF, adjustLSF, fetchPositions, alterLSF
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
def test_adjustLSF(setup):
    with app.test_request_context():
        term = Term.create(
            termCode=999999,
            termName="Test Term",
            termStart=date(2020, 7, 1),
            termEnd=date(2020, 12, 31),
            termState=True
        )
        student = Student.create(
            ID="B12345678",
            preferred_name="Nyan",
            legal_name="Nyan",
            LAST_NAME="Zaw",
            STU_EMAIL="imran@berea.edu"
        )
        dept = Department.create(
            DEPT_NAME="SSDT",
            ACCOUNT="SSDTACC",
            ORG="SSDTORG"
        )
        supervisor = Supervisor.create(ID="B12361006")
        supervisorOld = Supervisor.create(ID="B12365892")

        lsf = LaborStatusForm.create(
            laborStatusFormID=2,
            termCode=term,
            studentSupervisee=student,
            supervisor=supervisor,
            department=dept,
            jobType="Primary",
            WLS="OLDWLS",
            POSN_TITLE="Old Position",
            POSN_CODE="S61419",
            contractHours=40,
            weeklyHours=10,
            supervisorNotes="old notes."
        )
        LaborStatusForm.create(
            laborStatusFormID=2001,
            termCode=term,
            studentSupervisee=student,
            supervisor=supervisorOld,
            department=dept,
            jobType="Primary",
            WLS="OLDWLS",
            POSN_TITLE="Old Position Title",
            POSN_CODE="S61419"
        )

        # New position code row
        LaborStatusForm.create(
            laborStatusFormID=2002,
            termCode=term,
            studentSupervisee=student,
            supervisor=supervisorOld,
            department=dept,
            jobType="Primary",
            WLS="NEWWLS",
            POSN_TITLE="New Position Title",
            POSN_CODE="S61407"
        )

        fieldName = 'supervisorNotes'
        adjustLSF(fieldsChanged, fieldName, lsf, currentUser)
        assert Notes.get(Notes.notesContents == 'new notes.')

        fieldName = 'supervisor'
        adjustLSF(fieldsChanged, fieldName, lsf, currentUser)
        adjustedForm = AdjustedForm.get(AdjustedForm.fieldAdjusted == fieldName)
        assert adjustedForm.oldValue == 'B12361006'
        assert adjustedForm.newValue == 'B12365892'

        fieldName = 'position'
        adjustLSF(fieldsChanged, fieldName, lsf, currentUser)
        adjustedForm = AdjustedForm.get(AdjustedForm.fieldAdjusted == fieldName)
        assert adjustedForm.oldValue == 'S61419'
        assert adjustedForm.newValue == 'S61407'

        fieldName = 'weeklyHours'
        adjustLSF(fieldsChanged, fieldName, lsf, currentUser)
        adjustedForm = AdjustedForm.get(AdjustedForm.fieldAdjusted == fieldName)
        assert adjustedForm.oldValue == '10'
        assert adjustedForm.newValue == '12'

        # adjusted overload
        adjustLSF(fieldsChangedOverload, fieldName, lsf, currentUser)
        formHistory = FormHistory.get((FormHistory.formID == lsf.laborStatusFormID) &
                                      (FormHistory.historyType == 'Labor Overload Form'))
        adjustedForm = AdjustedForm.get(AdjustedForm.adjustedFormID == formHistory.adjustedForm)
        assert adjustedForm.oldValue == '10'
        assert adjustedForm.newValue == '20'
        assert formHistory.historyType.historyTypeName == 'Labor Overload Form'

        fieldName = 'contractHours'
        adjustLSF(fieldsChangedContractHours, fieldName, lsf, currentUser)
        adjustedForm = AdjustedForm.get(AdjustedForm.fieldAdjusted == fieldName)
        assert adjustedForm.oldValue == '40'
        assert adjustedForm.newValue == '60'

@pytest.mark.integration
def test_modifyLSF(setup):
    with mainDB.transaction() as transaction:

        term = Term.create(
            termCode=22332,
            termName="Test Term",
            termStart=date(2020, 7, 1),
            termEnd=date(2020, 12, 31),
            termState=True
        )
        student = Student.create(
            ID="B12332123",
            preferred_name="Nyan",
            legal_name="Nyan",
            LAST_NAME="Zaw",
            STU_EMAIL="imran@berea.edu"
        )
        dept = Department.create(
            DEPT_NAME="SSDT",
            ACCOUNT="SSDTACC",
            ORG="SSDTORG"
        )
        oldSupervisor = Supervisor.create(ID="B12361006")
        newSupervisor = Supervisor.create(ID="B12365892")
        lsf = LaborStatusForm.create(
            laborStatusFormID=98765,
            termCode=term,
            studentSupervisee=student,
            supervisor=oldSupervisor,
            department=dept,
            jobType="Primary",
            WLS="OLDWLS",
            POSN_TITLE="Old Position",
            POSN_CODE="S61419",
            contractHours=40,
            weeklyHours=10,
            supervisorNotes="old notes."
        )
        LaborStatusForm.create(
            laborStatusFormID=98766,
            termCode=term,
            studentSupervisee=student,
            supervisor=oldSupervisor,
            department=dept,
            jobType="Primary",
            WLS="OLDWLS",
            POSN_TITLE="Old Position Title",
            POSN_CODE="S61419"
        )
        LaborStatusForm.create(
            laborStatusFormID=98767,
            termCode=term,
            studentSupervisee=student,
            supervisor=oldSupervisor,
            department=dept,
            jobType="Primary",
            WLS="NEWWLS",
            POSN_TITLE="New Position Title",
            POSN_CODE="S61407"
        )

        with app.test_request_context():
            fieldName = 'supervisorNotes'
            modifyLSF(fieldsChanged, fieldName, lsf, currentUser)
            assert lsf.supervisorNotes == 'new notes.'

            fieldName = 'supervisor'
            modifyLSF(fieldsChanged, fieldName, lsf, currentUser)
            assert lsf.supervisor.ID == 'B12365892'

            fieldName = 'position'
            modifyLSF(fieldsChanged, fieldName, lsf, currentUser)
            assert lsf.POSN_CODE == 'S61407'

            fieldName = 'weeklyHours'
            modifyLSF(fieldsChanged, fieldName, lsf, currentUser)
            assert lsf.weeklyHours == 12

            modifyLSF(fieldsChangedOverload, fieldName, lsf, currentUser)
            assert lsf.weeklyHours == 20

            fieldName = 'contractHours'
            modifyLSF(fieldsChangedContractHours, fieldName, lsf, currentUser)
            assert lsf.contractHours == 60
        resetLSF()
        transaction.rollback()

@pytest.mark.integration
def test_createOverloadForm(setup):
    with app.test_request_context():
        newWeeklyHours = 20
        # modify lsf overload form
        createOverloadForm(newWeeklyHours, lsf, currentUser)
        # assert lsf.weeklyHours == 20  # There is a logical error here
        formHistory = FormHistory.get((FormHistory.formID == lsf.laborStatusFormID) & (FormHistory.historyType == 'Labor Overload Form'))
        assert formHistory.historyType.historyTypeName == 'Labor Overload Form'

        # adjust lsf overload form
        adjustedforms = AdjustedForm.create(fieldAdjusted = 'weeklyHours',
                                            oldValue      = '10',
                                            newValue      = newWeeklyHours,
                                            effectiveDate = datetime.strptime("07/21/2020", "%m/%d/%Y").strftime("%Y-%m-%d"))

        formHistories = FormHistory.create(formID       = lsf.laborStatusFormID,
                                           historyType  = "Labor Adjustment Form",
                                           adjustedForm = adjustedforms.adjustedFormID,
                                           createdBy    = currentUser,
                                           createdDate  = date.today(),
                                           status       = "Pending")

        createOverloadForm(newWeeklyHours, lsf, currentUser, adjustedforms.adjustedFormID, formHistories)
        adjustedForm = AdjustedForm.get(AdjustedForm.fieldAdjusted == 'weeklyHours')
        assert adjustedForm.oldValue == '10'
        assert adjustedForm.newValue == '20'
        formHistory = FormHistory.get((FormHistory.formID == lsf.laborStatusFormID) & (FormHistory.historyType == 'Labor Overload Form'))
        assert formHistory.historyType.historyTypeName == 'Labor Overload Form'

@pytest.mark.integration
def test_fetchPositions(setup):
    with mainDB.transaction() as transaction:
        deptOk = Department.create(DEPT_NAME="SSDT", ACCOUNT="SSDTACC", ORG="SSDTORG")
        deptOther = Department.create(DEPT_NAME="OTHER", ACCOUNT="OTHERACC", ORG="OTHERORG")
        term = Term.create(termCode=22332, termName="T", termStart="2020-07-01", termEnd="2020-12-31", termState=True)
        student = Student.create(ID="B1", preferred_name="N", legal_name="N", LAST_NAME="Z", STU_EMAIL="x@x.com")
        supervisor = Supervisor.create(ID="S1")
        lsfGood = LaborStatusForm.create(
            laborStatusFormID=98765,
            termCode=term,
            studentSupervisee=student,
            supervisor=supervisor,
            department=deptOk,
            jobType="Primary",
            WLS="W1",
            POSN_TITLE="Good Position",
            POSN_CODE="S61407",
            contractHours=40,
            weeklyHours=10,
            supervisorNotes="old notes."
        )
        lsfDummy = LaborStatusForm.create(
            laborStatusFormID=98766,
            termCode=term,
            studentSupervisee=student,
            supervisor=supervisor,
            department=deptOk,
            jobType="Primary",
            WLS="WD",
            POSN_TITLE="Dummy Position",
            POSN_CODE="S12345",
            contractHours=40,
            weeklyHours=10,
            supervisorNotes="old notes."
        )
        lsfOther = LaborStatusForm.create(
            laborStatusFormID=98767,
            termCode=term,
            studentSupervisee=student,
            supervisor=supervisor,
            department=deptOther,
            jobType="Primary",
            WLS="Wo",
            POSN_TITLE="Other Dept Position",
            POSN_CODE="S99999",
            contractHours=40,
            weeklyHours=10,
            supervisorNotes="old notes."
        )
        status_obj, _ = Status.get_or_create(statusName="Approved")  
        history_type_obj, _ = HistoryType.get_or_create(historyTypeName="Labor Status Form")  
        currentUser = User.get(User.userID == 3)
        FormHistory.create(
            formID=lsfGood,
            historyType=history_type_obj,
            createdBy=currentUser,
            createdDate=date.today(),
            status=status_obj
        )
        FormHistory.create(
            formID=lsfDummy,
            historyType=history_type_obj,
            createdBy=currentUser,
            createdDate=date.today(),
            status=status_obj
        )
        FormHistory.create(
            formID=lsfOther,
            historyType=history_type_obj,
            createdBy=currentUser,
            createdDate=date.today(),
            status=status_obj
        )

        with app.test_request_context():
            positions = json.loads(fetchPositions("SSDTORG", "SSDTACC"))
            assert "S61407" in positions
            assert positions["S61407"]["POSN_TITLE"] == "Good Position"
            assert positions["S61407"]["WLS"] == "W1"
            assert positions["S61407"]["POSN_CODE"] == "S61407"
            assert "S12347" not in positions
            assert "S99999" not in positions

        resetLSF()
        transaction.rollback()

@pytest.mark.integration
def test_alterLSF(setup):
    with mainDB.transaction() as transaction:
        deptOk = Department.create(DEPT_NAME="SSDT", ACCOUNT="SSDTACC", ORG="SSDTORG")
        deptOther = Department.create(DEPT_NAME="OTHER", ACCOUNT="OTHERACC", ORG="OTHERORG")
        term = Term.create(
            termCode=22332,
            termName="T",
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
            with renderedTemplate(app) as templates:
                alterLSF(lsfGood.laborStatusFormID)
            template, ctx = templates[0]
            supervisors = [s.ID for s in ctx["supervisors"]]
            assert "B12361006" in supervisors
            assert "B12365892" in supervisors
            departments = {d.departmentID for d in ctx["departments"]}
            assert deptOk.departmentID in departments
            assert deptOther.departmentID in departments
            positions = ctx["positions"]
            positionIDs = {
                p.formID.laborStatusFormID if hasattr(p, "formID")
                else p.laborStatusFormID
                for p in positions
            }
            assert lsfGood.laborStatusFormID in positionIDs
            assert lsfDummy.laborStatusFormID in positionIDs
            assert lsfOther.laborStatusFormID not in positionIDs
        resetLSF()
        transaction.rollback()

@contextmanager
def renderedTemplate(app):
    recorded = []
    def record(sender, template, context, **extra):
        recorded.append((template, context))
    
    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)