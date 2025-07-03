from datetime import date, datetime
from app.models.notes import Notes
from app.models.department import Department
from app.models.adjustedForm import AdjustedForm
from app.controllers.main_routes.laborHistory import *
from app.logic.emailHandler import *
from app.logic.utils import makeThirdPartyLink
from app.logic.userInsertFunctions import createSupervisorFromTracy
from app.logic.tracy import Tracy



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
        supervisor = createSupervisorFromTracy(bnumber=fieldsChanged[fieldName]["newValue"])
        lsf.supervisor = supervisor.ID
        lsf.save()

    if fieldName == "department":
        department = Department.get(Department.ORG==fieldsChanged[fieldName]['newValue'])
        lsf.department = department.departmentID
        lsf.save()

    if fieldName == "position":
        position = Tracy().getPositionFromCode(fieldsChanged[fieldName]["newValue"])
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
    

def createOverloadForm(newWeeklyHours, lsf, currentUser, adjustedForm=None,  formHistories=None, host=None):
    allTermForms = LaborStatusForm.select() \
                   .join_from(LaborStatusForm, Student) \
                   .join_from(LaborStatusForm, FormHistory) \
                   .where((LaborStatusForm.termCode == lsf.termCode) &
                         (LaborStatusForm.studentSupervisee.ID == lsf.studentSupervisee.ID) &
                         ~(FormHistory.status % "Denied%") &
                         (FormHistory.historyType == "Labor Status Form"))


    previousTotalHours = 0
    if allTermForms:
        for statusForm in allTermForms:
            previousTotalHours += statusForm.weeklyHours
    changeInHours = newWeeklyHours - lsf.weeklyHours
    newTotalHours = previousTotalHours + changeInHours

    if previousTotalHours <= 15 and newTotalHours > 15:  # If we weren't overloading and now we are
        newLaborOverloadForm = OverloadForm.create(studentOverloadReason = "None")
        newFormHistory = FormHistory.create(formID       = lsf.laborStatusFormID,
                                            historyType  = "Labor Overload Form",
                                            createdBy    = currentUser,
                                            adjustedForm = adjustedForm,
                                            overloadForm = newLaborOverloadForm.overloadFormID,
                                            createdDate  = date.today(),
                                            status       = "Pre-Student Approval")
        try:
            if formHistories:
                formHistories.status = "Pre-Student Approval"
                formHistories.save()

            else:
                modifiedFormHistory = FormHistory.select() \
                                    .join_from(FormHistory, HistoryType) \
                                    .where(FormHistory.formID == lsf.laborStatusFormID, FormHistory.historyType.historyTypeName == "Labor Status Form") \
                                    .get()
                modifiedFormHistory.status = "Pre-Student Approval"
                modifiedFormHistory.save()

            link = makeThirdPartyLink("student", host, newFormHistory.formHistoryID)
            overloadEmail = emailHandler(newFormHistory.formHistoryID)
            overloadEmail.LaborOverLoadFormSubmitted(link)

        except Exception as e:
            print("An error occured while attempting to send overload form emails: ", e)

    # This will delete an overload form after the hours are changed
    elif previousTotalHours > 15 and newTotalHours <= 15:  # If we were overloading and now we aren't
            print(f"Trying to get formhistory with formID '{lsf.laborStatusFormID}' and history type: 'Labor Overload Form'")
            deleteOverloadForm = FormHistory.get((FormHistory.formID == lsf.laborStatusFormID) & (FormHistory.historyType == "Labor Overload Form"))
            deleteOverloadForm = OverloadForm.get(OverloadForm.overloadFormID == deleteOverloadForm.overloadForm_id)
            deleteOverloadForm.delete_instance()  # This line also deletes the Form History since it's set to cascade up in the model file
