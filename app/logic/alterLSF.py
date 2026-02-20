from datetime import date, datetime
from app.models.notes import Notes
from app.models.department import Department
from app.models.adjustedForm import AdjustedForm
from app.controllers.main_routes.laborHistory import *
from app.logic.emailHandler import *
from app.logic.utils import makeThirdPartyLink
from app.logic.userInsertFunctions import createSupervisorFromTracy
from app.logic.tracy import Tracy
from app.logic.statusFormFunctions import createOverloadForm


def modifyLSF(fieldsChanged, fieldName, lsf, currentUser, host=None):
    if fieldName == "supervisorNotes":
        noteEntry = Notes.create(formID           = lsf.laborStatusFormID,
                                         createdBy     = currentUser,
                                         date          = datetime.now().strftime("%Y-%m-%d"),
                                         notesContents = fieldsChanged[fieldName]["newValue"],
                                         noteType      = "Supervisor Note")
        noteEntry.save()
        lsf.supervisorNotes = noteEntry.notesContents
        lsf.save()
    if fieldName == "supervisor":
        supervisor = Supervisor.get(Supervisor.ID == fieldsChanged[fieldName]["newValue"])
        lsf.supervisor = supervisor.ID
        lsf.save()

    if fieldName == "department":
        department = Department.get(Department.ORG==fieldsChanged[fieldName]['newValue'])
        lsf.department = department.departmentID
        lsf.save()

    if fieldName == "position":
        position = (
            LaborStatusForm
            .select(LaborStatusForm.POSN_CODE)
            .where(LaborStatusForm.POSN_CODE == fieldsChanged[fieldName]["newValue"])
            .first()
        )        
        lsf.POSN_CODE = position.POSN_CODE
        lsf.POSN_TITLE = position.POSN_TITLE
        lsf.WLS = position.WLS
        lsf.save()

    if fieldName == "weeklyHours":
        newWeeklyHours = int(fieldsChanged[fieldName]['newValue'])
        createOverloadForm(newWeeklyHours, lsf, currentUser, host=host)
        lsf.weeklyHours = newWeeklyHours
        lsf.save()

    if fieldName == "contractHours":
        lsf.contractHours = int(fieldsChanged[fieldName]["newValue"])
        lsf.save()

    if fieldName == "startDate":
        lsf.startDate = datetime.strptime(fieldsChanged[fieldName]["newValue"], "%m/%d/%Y").strftime('%Y-%m-%d')
        lsf.save()

    if fieldName == "endDate":
        lsf.endDate = datetime.strptime(fieldsChanged[fieldName]["newValue"], "%m/%d/%Y").strftime('%Y-%m-%d')
        lsf.save()


def adjustLSF(fieldsChanged, fieldName, lsf, currentUser, host=None):
    if fieldName == "supervisorNotes":
        newNoteEntry = Notes.create(formID        = lsf.laborStatusFormID,
                                         createdBy     = currentUser,
                                         date          = datetime.now().strftime("%Y-%m-%d"),
                                         notesContents = fieldsChanged[fieldName]["newValue"],
                                         noteType      = "Supervisor Note")
        newNoteEntry.save()
        return None
    else:
        adjustedforms = AdjustedForm.create(fieldAdjusted = fieldName,
                                            oldValue      = fieldsChanged[fieldName]["oldValue"],
                                            newValue      = fieldsChanged[fieldName]["newValue"],
                                            effectiveDate = datetime.strptime(fieldsChanged[fieldName]["date"], "%m/%d/%Y").strftime("%Y-%m-%d"))
        historyType = HistoryType.get(HistoryType.historyTypeName == "Labor Adjustment Form")
        status = Status.get(Status.statusName == "Pending")
        adjustedFormHistory = FormHistory.create(formID       = lsf.laborStatusFormID,
                                           historyType  = historyType.historyTypeName,
                                           adjustedForm = adjustedforms.adjustedFormID,
                                           createdBy    = currentUser,
                                           createdDate  = date.today(),
                                           status       = status.statusName)
        
        if fieldName == "weeklyHours":
            newWeeklyHours = int(fieldsChanged[fieldName]['newValue'])
            createOverloadForm(newWeeklyHours, lsf, currentUser, adjustedforms.adjustedFormID, adjustedFormHistory,host=host)

        return adjustedFormHistory.formHistoryID
    
