import json
from datetime import date
from flask import jsonify, g, flash
from app.models.formHistory import FormHistory
from app.models.status import Status
from app.logic.banner import Banner
from app.logic.emailHandler import emailHandler
from app.login_manager import require_login
from app.models.laborStatusForm import LaborStatusForm
from app.models.supervisor import Supervisor
from app.models.department import Department
from app.logic.userInsertFunctions import createSupervisorFromTracy
from app.logic.tracy import Tracy
from app.models.overloadForm import OverloadForm
from app.models.notes import Notes
from app.login_manager import DoesNotExist, render_template
from app.logic.allocation import getAllocationWarning


def saveStatus(new_status, formHistoryIds, currentUser):
    approvedDepartments = {}
    try:
        if new_status == 'Denied by Admin':
            # Index 1 will always hold the reject reason in the list, so we can
            # set a variable equal to the index value and then slice off the list
            # item before the iteration
            denyReason = formHistoryIds[1]
            formHistoryIds = formHistoryIds[:1]

        for formHistoryID in formHistoryIds:
            formHistory = FormHistory.get(FormHistory.formHistoryID == formHistoryID)
            formHistory.status = Status.get(Status.statusName == new_status)
            
            formHistory.reviewedDate = date.today()
            formHistory.reviewedBy = currentUser

            formType = formHistory.historyType_id

            # Add a note if we've skipped to Pending
            if new_status == 'Pending':
                note = "Skipped Student Approval"
                Notes.create(formID=formHistory.formID,
                             createdBy=currentUser,
                             date=date.today(),
                             notesContents=note,
                             noteType = "Labor Note")


            # Add to BANNER
            save_status = True # default true so that we will still save in other cases

            if new_status == 'Approved' and formType == "Labor Status Form" and formHistory.formID.POSN_CODE != "S12345": # don't update banner for Adjustment forms or for CS dummy position
                if formHistory.formID.POSN_CODE == "SNOLAB":
                       formHistory.formID.weeklyHours = 10
                conn = Banner()
                save_status = conn.insert(formHistory)

            # if we are able to save
            if save_status:

                if new_status == 'Denied by Admin':
                    formHistory.rejectReason = denyReason
                formHistory.save()

                # Send necessary emails from the status change
                email = emailHandler(formHistory.formHistoryID)
                if new_status == "Denied by Admin" and formType == "Labor Status Form":
                    email.laborStatusFormRejected()
                if new_status == "Approved" and formType == "Labor Status Form":
                    email.laborStatusFormApproved()
                    dept = formHistory.formID.department
                    approvedDepartments[dept.departmentID] = dept
                if new_status == "Approved" and formType == "Labor Adjustment Form":
                    # This function is triggered whenever an adjustment form is approved.
                    # The following function overrides the original data in lsf with the new data from adjustment form.
                    LSF = LaborStatusForm.get_by_id(formHistory.formID)
                    overrideOriginalStatusFormOnAdjustmentFormApproval(formHistory, LSF)

            else:
                print("Unable to update form status for formHistoryID {}.".format(id))
                return jsonify({"success": False}), 500

    except Exception as e:
        print("Error preparing form for status update:", e)
        return jsonify({"success": False}), 500

    # After approving, let the admin know right away if any affected department
    # is now over its allocated positions or break hours (informational only).
    for dept in approvedDepartments.values():
        warning = getAllocationWarning(dept, g.openTerm)
        if warning and warning['isOverAllocated']:
            messageParts = [f"{b['label']} ({b['used']}/{b['allocated']})" for b in warning['overAllocatedBands']]
            if warning['isBreakHoursOverAllocated']:
                messageParts.append(f"break hours ({warning['breakHoursUsed']}/{warning['breakHoursAllocated']})")
            flash(f"{dept.DEPT_NAME} is now over its allocation for: {', '.join(messageParts)}.", "warning")

    return jsonify({"success": True})

def overrideOriginalStatusFormOnAdjustmentFormApproval(form, LSF):
    """
    This function checks whether an Adjustment Form is approved. If yes, it overrides the information
    in the original Labor Status Form with the new information coming from approved Adjustment Form.

    The only fields that will ever be changed in an adjustment form are: supervisor, department, position, and hours.
    """
    currentUser = require_login()
    if not currentUser:        # Not logged in
            return render_template('errors/403.html'), 403
    if form.adjustedForm.fieldAdjusted == "supervisor":
        d, created = Supervisor.get_or_create(ID = form.adjustedForm.newValue)
        if not created:
            LSF.supervisor = d.ID
        LSF.save()
        if created:
            tracyUser = Tracy().getSupervisorFromID(form.adjustedForm.newValue)
            tracyEmail = tracyUser.EMAIL
            tracyUsername = tracyEmail.find('@')
            createSupervisorFromTracy(tracyUsername)

    if form.adjustedForm.fieldAdjusted == "position":
        LSF.POSN_CODE = form.adjustedForm.newValue
        position = Tracy().getPositionFromCode(form.adjustedForm.newValue)
        LSF.POSN_TITLE = position.POSN_TITLE
        LSF.WLS = position.WLS
        LSF.save()

    if form.adjustedForm.fieldAdjusted == "department":
        department = Department.get(Department.ORG==form.adjustedForm.newValue)
        LSF.department = department.departmentID
        LSF.save()

    if form.adjustedForm.fieldAdjusted == "contractHours":
        LSF.contractHours = int(form.adjustedForm.newValue)
        LSF.save()

    if form.adjustedForm.fieldAdjusted == "weeklyHours":
        LSF.weeklyHours = int(form.adjustedForm.newValue)
        LSF.save()


def laborAdminOverloadApproval(rsp, historyForm, status, currentUser, currentDate, email):
    if rsp['formType'] == 'Overload':
        overloadForm = OverloadForm.get(OverloadForm.overloadFormID == historyForm.overloadForm.overloadFormID)
        overloadForm.laborApproved = status
        overloadForm.laborApprover = currentUser
        overloadForm.laborReviewDate = currentDate
        overloadForm.save()
        try:
            pendingForm = FormHistory.select().where((FormHistory.formID == historyForm.formID) & (FormHistory.status == "Pending") & (FormHistory.historyType != "Labor Overload Form")).get()
            if historyForm.adjustedForm and rsp['status'] == "Approved":
                LSF = LaborStatusForm.get(LaborStatusForm.laborStatusFormID == historyForm.formID)
                if historyForm.adjustedForm.fieldAdjusted == "weeklyHours":
                    LSF.weeklyHours = pendingForm.adjustedForm.newValue
                    LSF.save()
            if pendingForm.historyType.historyTypeName == "Labor Status Form" or (pendingForm.historyType.historyTypeName == "Labor Adjustment Form" and pendingForm.adjustedForm.fieldAdjusted == "weeklyHours"):
                pendingForm.status = status
                pendingForm.reviewedBy = currentUser
                pendingForm.reviewedDate = currentDate
                if 'denialReason' in rsp.keys():
                    pendingForm.rejectReason = rsp['denialReason']
                    Notes.create(formID = pendingForm.formID.laborStatusFormID,
                                    createdBy = currentUser,
                                    date = currentDate,
                                    notesContents = rsp['denialReason'],
                                    noteType = "Labor Note")
                pendingForm.save()

                if pendingForm.historyType.historyTypeName == "Labor Status Form":
                    email = emailHandler(pendingForm.formHistoryID)
                    if rsp['status'] == 'Approved':
                        email.laborStatusFormApproved()
                    elif rsp['status'] == 'Denied by Admin':
                        email.laborStatusFormRejected()
        except DoesNotExist:
            pass
        except Exception as e:
            print(e)
    if 'denialReason' in rsp.keys():
        # We only update the reject reason if one was given on the UI
        historyForm.rejectReason = rsp['denialReason']
        historyForm.save()
        Notes.create(formID = historyForm.formID.laborStatusFormID,
                        createdBy = currentUser,
                        date = currentDate,
                        notesContents = rsp['denialReason'],
                        noteType = "Labor Note")
    if 'adminNotes' in rsp.keys():
        # We only add admin notes if there was a note made on the UI
        Notes.create(formID = historyForm.formID.laborStatusFormID,
                        createdBy = currentUser,
                        date = currentDate,
                        notesContents = rsp['adminNotes'],
                        noteType = "Labor Note")
    historyForm.status = status.statusName
    historyForm.reviewedBy = currentUser
    historyForm.reviewedDate = currentDate
    historyForm.save()
    if rsp['formType'] == 'Overload':
        if rsp['status'] == 'Approved':
            email.LaborOverLoadFormApproved()
        elif rsp['status'] == 'Denied by Admin':
            email.LaborOverLoadFormRejected()
    elif rsp['formType'] == 'Release':
        if rsp['status'] == 'Approved':
            email.laborReleaseFormApproved()
        elif rsp['status'] == 'Denied by Admin':
            email.laborReleaseFormRejected()
    return jsonify({"Success": True})


# extract data from the database to populate pending form approval modal
def modal_approval_and_denial_data(formHistoryIdList):
    details_list = []
    allocationWarningsByDept = {}
    for fhID in formHistoryIdList:
        formHistory = FormHistory.get(FormHistory.formHistoryID == fhID)
        lsf = formHistory.formID

        studentName = f"{lsf.studentSupervisee.FIRST_NAME} {lsf.studentSupervisee.LAST_NAME}"
        position = lsf.POSN_TITLE
        supervisorName = f"{lsf.supervisor.FIRST_NAME} {lsf.supervisor.LAST_NAME}"
        weeklyHours = lsf.weeklyHours
        contractHours = lsf.contractHours
        dept = lsf.department
        deptName = dept.DEPT_NAME

        if formHistory.adjustedForm:
            match formHistory.adjustedForm.fieldAdjusted:
                case "position":
                    position = Tracy().getPositionFromCode(formHistory.adjustedForm.newValue)
                    position = position.POSN_TITLE
                case "supervisor":
                    supervisor = Supervisor.get(Supervisor.ID == formHistory.adjustedForm.newValue)
                    supervisorName = f"{supervisor.FIRST_NAME} {supervisor.LAST_NAME}"
                case "weeklyHours":
                    weeklyHours = formHistory.adjustedForm.newValue
                case "contractHours":
                    contractHours = formHistory.adjustedForm.newValue
                case "department":
                    dept = Department.get(Department.ORG==formHistory.adjustedForm.newValue)
                    deptName = dept.DEPT_NAME

        details_list.append([studentName, deptName, position, str(weeklyHours),str(contractHours), supervisorName])

        if dept.departmentID not in allocationWarningsByDept:
            warning = getAllocationWarning(dept, g.openTerm)
            if warning:
                allocationWarningsByDept[dept.departmentID] = warning

    return {"details": details_list, "allocationWarnings": list(allocationWarningsByDept.values())}


def financialAidSAASOverloadApproval(historyForm, rsp, status, currentUser, currentDate):
    selectedOverload = OverloadForm.get(OverloadForm.overloadFormID == historyForm.overloadForm.overloadFormID)
    if 'denialReason' in rsp.keys():
        newNoteEntry = Notes.create(formID=historyForm.formID.laborStatusFormID,
                                    createdBy=currentUser,
                                    date=currentDate,
                                    notesContents=rsp["denialReason"],
                                    noteType = "Labor Note")
        newNoteEntry.save()
    ## Updating the overloadform TableS
    if currentUser.isFinancialAidAdmin:
        selectedOverload.financialAidApproved = status.statusName
        selectedOverload.financialAidApprover = currentUser
        selectedOverload.financialAidInitials = rsp['initials']
        selectedOverload.financialAidReviewDate = currentDate

    elif currentUser.isSaasAdmin:
        selectedOverload.SAASApproved = status.statusName
        selectedOverload.SAASApprover = currentUser
        selectedOverload.SAASInitials = rsp['initials']
        selectedOverload.SAASReviewDate = currentDate
    selectedOverload.save()
    return jsonify({"Success": True})


def checkAdjustment(allForms):
    """
        Retrieve `supervisor` and position information for adjusted forms using the new values
        stored in adjusted table and update allForms
    """
    if allForms.adjustedForm:

        if allForms.adjustedForm.fieldAdjusted == "supervisor":
            # use the supervisor id in the field adjusted to find supervisor in User table.
            newSupervisorID = allForms.adjustedForm.newValue
            newSupervisor = Supervisor.get(Supervisor.ID == newSupervisorID)
            if not newSupervisor:
                newSupervisor = createSupervisorFromTracy(bnumber=newSupervisorID)

            # we are temporarily storing the supervisor name in new value,
            # because we want to show the supervisor name in the hmtl template.
            allForms.adjustedForm.newValue = newSupervisor.FIRST_NAME +" "+ newSupervisor.LAST_NAME
            allForms.adjustedForm.oldValue = {"email":newSupervisor.EMAIL, "ID":newSupervisor.ID}

        if allForms.adjustedForm.fieldAdjusted == "position":
            newPositionCode = allForms.adjustedForm.newValue
            newPosition = Tracy().getPositionFromCode(newPositionCode)
            # temporarily storing the position code and wls in new value, and position name in old value
            # because we want to show these information in the hmtl template.
            allForms.adjustedForm.newValue = newPosition.POSN_CODE +" (" + newPosition.WLS+")"
            allForms.adjustedForm.oldValue = newPosition.POSN_TITLE

        if allForms.adjustedForm.fieldAdjusted == "department":
            newDepartment = Department.get_or_none(Department.ORG == allForms.adjustedForm.newValue)
            
            if newDepartment:
                allForms.adjustedForm.newValue = newDepartment.DEPT_NAME
            else:
                allForms.adjustedForm.newValue = "Unknown - " + allForms.adjustedForm.newValue

            oldDepartment = Department.get_or_none(Department.ORG == allForms.adjustedForm.oldValue)
            if oldDepartment:
                allForms.adjustedForm.oldValue = oldDepartment.ORG + "-" + oldDepartment.ACCOUNT
            else:
                allForms.adjustedForm.oldValue = "Unknown - " + allForms.adjustedForm.oldValue