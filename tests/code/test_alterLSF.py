import pytest
from app import app
from app.controllers.main_routes.alterLSF import modifyLSF, adjustLSF
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
    with mainDB.atomic() as transaction:
        print("we ar ehere")
        term = Term.create(
            termCode=22332,
            termName="Test Term",
            termStart=date(2020, 7, 1),
            termEnd=date(2020, 12, 31),
            termState=True
        )
        print("we ar ehere")
        student = Student.create(
            ID="B12332123",
            preferred_name="Nyan",
            legal_name="Nyan",
            LAST_NAME="Zaw",
            STU_EMAIL="imran@berea.edu"
        )
        print("we ar ehere")
        dept = Department.create(
            DEPT_NAME="SSDT",
            ACCOUNT="SSDTACC",
            ORG="SSDTORG"
        )
        print("we ar ehere")
        oldSupervisor = Supervisor.get_or_none(Supervisor.ID == "B12361006")
        if oldSupervisor is None:
            oldSupervisor = Supervisor.create(ID="B12361006")
        newSupervisor = Supervisor.get_or_none(Supervisor.ID == "B12365892")
        if newSupervisor is None:
            newSupervisor = Supervisor.create(ID="B12365892")
        print("we ar ehere")
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
        print("we ar ehere")
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
        print("we ar ehere")
        with app.test_request_context():
            print("we ar ehere")
            fieldName = 'supervisorNotes'
            modifyLSF(fieldsChanged, fieldName, lsf, currentUser)
            assert lsf.supervisorNotes == 'new notes.'
            print("here1")
            fieldName = 'supervisor'
            modifyLSF(fieldsChanged, fieldName, lsf, currentUser)
            assert lsf.supervisor.ID == 'B12365892'
            print("here2")
            fieldName = 'position'
            modifyLSF(fieldsChanged, fieldName, lsf, currentUser)
            print("chichcc", lsf.POSN_CODE)
            assert lsf.POSN_CODE == 'S61407'
            print("here3")
            fieldName = 'weeklyHours'
            modifyLSF(fieldsChanged, fieldName, lsf, currentUser)
            assert lsf.weeklyHours == 12
            print("here4")
            # Modified verload
            modifyLSF(fieldsChangedOverload, fieldName, lsf, currentUser)
            assert lsf.weeklyHours == 20
            print("FH rows for this formID:",
                list(FormHistory
                    .select(FormHistory.formHistoryID, FormHistory.formID)
                    .where(FormHistory.formID == lsf.laborStatusFormID)
                    .dicts()))

            print("FH last 10 rows (id, formID):",
                list(FormHistory
                    .select(FormHistory.formHistoryID, FormHistory.formID)
                    .order_by(FormHistory.formHistoryID.desc())
                    .limit(10)
                    .dicts()))
            print("here4.5")
            print("fiofi", lsf.laborStatusFormID)
            formHistory = ( FormHistory.select().join(HistoryType)
                           .where((FormHistory.formID == lsf.laborStatusFormID) 
                                  & (HistoryType.historyTypeName == 'Labor Overload Form'))
                .get_or_none()
            )
            print(formHistory,"fiofi", lsf.laborStatusFormID)
            assert formHistory.historyType.historyTypeName == 'Labor Overload Form'
            print("here5")
            fieldName = 'contractHours'
            modifyLSF(fieldsChangedContractHours, fieldName, lsf, currentUser)
            assert lsf.contractHours == 60
            print("here6")
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
