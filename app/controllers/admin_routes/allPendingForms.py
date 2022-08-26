from flask import flash, send_file, json, jsonify, redirect, url_for, abort
from peewee import JOIN
from app.login_manager import *
from app.controllers.admin_routes import admin
from app.controllers.errors_routes.handlers import *
from app.models.laborReleaseForm import LaborReleaseForm
from app.models.laborStatusForm import LaborStatusForm
from app.models.adjustedForm import AdjustedForm
from app.models.emailTracker import EmailTracker
from app.models.overloadForm import OverloadForm
from app.models.notes import Notes
from app.logic.emailHandler import *
from app.logic.utils import makeThirdPartyLink
from app.models.formHistory import *
from app.models.term import Term
from app.logic.banner import Banner
from app.logic.tracy import Tracy
from app import cfg
from datetime import datetime, date
from flask import Flask, redirect, url_for, flash
from app.models.Tracy.stuposn import STUPOSN
from app.models.supervisor import Supervisor
from app.models.historyType import HistoryType
from app.models.department import Department
from app.controllers.main_routes.download import CSVMaker


@admin.route('/admin/pendingForms/<formType>',  methods=['GET'])
def allPendingForms(formType):
    try:
        global globalFormType
        globalFormType = formType
        currentUser = require_login()
        if not currentUser:                    # Not logged in
            return render_template('errors/403.html'), 403
        if not currentUser.isLaborAdmin:       # Not an admin
            if currentUser.student: # logged in as a student
                return redirect('/laborHistory/' + currentUser.student.ID)
            elif currentUser.supervisor and not currentUser.isFinancialAidAdmin and not currentUser.isSaasAdmin:
                return render_template('errors/403.html'), 403
        formList = None
        historyType = None
        pageTitle = ""
        approvalTarget = ""
        completedOverloadFormCounter = 0
        laborStatusFormCounter = FormHistory.select().where(((FormHistory.status == "Pending")|(FormHistory.status == 'Pre-Student Approval')) & (FormHistory.historyType == 'Labor Status Form')).count()
        adjustedFormCounter = FormHistory.select().where(((FormHistory.status == 'Pending')|(FormHistory.status == 'Pre-Student Approval')) & (FormHistory.historyType == 'Labor Adjustment Form')).count()
        releaseFormCounter = FormHistory.select().where((FormHistory.status == 'Pending') & (FormHistory.historyType == 'Labor Release Form')).count()

        if currentUser.isLaborAdmin:
            overloadFormCounter = FormHistory.select().where(((FormHistory.status == 'Pending')|(FormHistory.status == 'Pre-Student Approval')) & (FormHistory.historyType == 'Labor Overload Form')).count()
        elif currentUser.isFinancialAidAdmin:
            overloadFormCounter = FormHistory.select().join_from(FormHistory, OverloadForm)\
                                             .where((FormHistory.status == 'Pending') & (FormHistory.historyType == 'Labor Overload Form'))\
                                             .where((FormHistory.overloadForm.financialAidApproved == 'Pending') | (FormHistory.overloadForm.financialAidApproved == None)).count()

            completedOverloadFormCounter = FormHistory.select().join_from(FormHistory, OverloadForm)\
                                                     .where(FormHistory.historyType == 'Labor Overload Form')\
                                                     .where((FormHistory.overloadForm.financialAidApproved == 'Approved') | (FormHistory.overloadForm.financialAidApproved == 'Denied')).count()
        elif currentUser.isSaasAdmin:
            overloadFormCounter = FormHistory.select().join_from(FormHistory, OverloadForm)\
                                             .where((FormHistory.status == 'Pending') & (FormHistory.historyType == 'Labor Overload Form'))\
                                             .where((FormHistory.overloadForm.SAASApproved == 'Pending') | (FormHistory.overloadForm.SAASApproved == None)).count()

            completedOverloadFormCounter = FormHistory.select().join_from(FormHistory, OverloadForm)\
                                                     .where(FormHistory.historyType == 'Labor Overload Form')\
                                                     .where((FormHistory.overloadForm.SAASApproved == 'Approved') | (FormHistory.overloadForm.SAASApproved == 'Denied')).count()

        if formType == "pendingLabor":
            historyType = "Labor Status Form"
            approvalTarget = "denyLaborStatusFormsModal"
            pageTitle = "Pending Labor Status Forms"

        elif formType == "pendingAdjustment":
            historyType = "Labor Adjustment Form"
            approvalTarget = "denyAdjustedFormsModal"
            pageTitle = "Pending Adjustment Forms"

        elif formType == "pendingOverload":
            historyType = "Labor Overload Form"
            approvalTarget = "denyOverloadFormsModal"
            pageTitle = "Pending Overload Forms"

        elif formType == "pendingRelease":
            historyType = "Labor Release Form"
            approvalTarget = "denyReleaseformSModal"
            pageTitle = "Pending Release Forms"

        elif formType == "completedOverload":
            historyType = "Labor Overload Form"
            approvalTarget = ""
            pageTitle = "Approved Overload Forms"

        # We are adding all of these joins so we don't do 10 queries later for every form
        CreatorSup = Supervisor.alias()
        baseQuery = (FormHistory.select(FormHistory, OverloadForm, LaborStatusForm, Supervisor, Student, User, Department, Term, CreatorSup, HistoryType, Status)
                                .join(OverloadForm, JOIN.LEFT_OUTER).switch()
                                .join(HistoryType).switch()
                                .join(LaborStatusForm)
                                .join(Supervisor).switch(LaborStatusForm)
                                .join(Student).switch(LaborStatusForm)
                                .join(Department).switch(LaborStatusForm)
                                .join(Term).switch()
                                .join(Status).switch()
                                .join(User, attr="createdBy", on=(FormHistory.createdBy == User.userID))
                                .join(CreatorSup, JOIN.LEFT_OUTER, attr="supervisor", on=(User.supervisor == CreatorSup.ID))
                                )
        if currentUser.isFinancialAidAdmin:
            if formType == "pendingOverload":
                baseQuery = (baseQuery.where((FormHistory.status == 'Pending'))
                                      .where(FormHistory.historyType == "Labor Overload Form")
                                      .where((FormHistory.overloadForm.financialAidApproved == 'Pending') | (FormHistory.overloadForm.financialAidApproved == None))
                                      )
            elif formType == "completedOverload":
                baseQuery = (baseQuery.where(FormHistory.historyType == "Labor Overload Form")
                                      .where((FormHistory.overloadForm.financialAidApproved == 'Approved') | (FormHistory.overloadForm.financialAidApproved == 'Denied'))
                                      )

        if currentUser.isSaasAdmin:
            if formType == "pendingOverload":
                baseQuery = (baseQuery.where(FormHistory.status == 'Pending')
                                      .where(FormHistory.historyType == "Labor Overload Form")
                                      .where((FormHistory.overloadForm.SAASApproved == 'Pending') | (FormHistory.overloadForm.SAASApproved == None)))
            elif formType == "completedOverload":
                baseQuery = (baseQuery.where(FormHistory.historyType == "Labor Overload Form")
                                      .where((FormHistory.overloadForm.SAASApproved == 'Approved') | (FormHistory.overloadForm.SAASApproved == 'Denied')))

        if currentUser.isLaborAdmin:
            baseQuery = baseQuery.where((FormHistory.status == "Pending")|(FormHistory.status == 'Pre-Student Approval'), FormHistory.historyType == historyType)

        formList = baseQuery.order_by(-FormHistory.createdDate).distinct()

        # only if a form is adjusted
        pendingOverloadFormPairs = {}
        # or allForms.adjustedForm.fieldAdjusted == "Weekly Hours":
        for allForms in formList:
            if allForms.historyType.historyTypeName == "Labor Status Form" or (allForms.historyType.historyTypeName == "Labor Adjustment Form" and allForms.adjustedForm.fieldAdjusted == "weeklyHours"):
                try:
                    overloadForm = FormHistory.select().where((FormHistory.formID == allForms.formID) & (FormHistory.historyType == "Labor Overload Form") & ((FormHistory.status == "Pending") | (FormHistory.status == "Pre-Student Approval"))).get()
                    if overloadForm:
                        pendingOverloadFormPairs[allForms.formHistoryID] = overloadForm.formHistoryID
                except DoesNotExist:
                    pass
                except Exception as e:
                    print(e)

            checkAdjustment(allForms)

        return render_template( 'admin/allPendingForms.html',
                                title=pageTitle,
                                username=currentUser.username,
                                formList = formList,
                                formType= formType,
                                modalTarget = approvalTarget,
                                overloadFormCounter = overloadFormCounter,
                                laborStatusFormCounter = laborStatusFormCounter,
                                adjustedFormCounter  = adjustedFormCounter,
                                releaseFormCounter = releaseFormCounter,
                                completedOverloadFormCounter = completedOverloadFormCounter,
                                pendingOverloadFormPairs = pendingOverloadFormPairs
                                )
    except Exception as e:
        print("Error Loading all Pending Forms:", e)
        return render_template('errors/500.html'), 500

def checkAdjustment(allForms):
    """
        Retrieve supervisor and position information for adjusted forms using the new values
        stored in adjusted table and update allForms
    """
    if allForms.adjustedForm:

        if allForms.adjustedForm.fieldAdjusted == "supervisor":
            # use the supervisor id in the field adjusted to find supervisor in User table.
            newSupervisorID = allForms.adjustedForm.newValue
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
            newDepartment = Department.get(Department.ORG==allForms.adjustedForm.newValue)
            allForms.adjustedForm.newValue = newDepartment.DEPT_NAME
            allForms.adjustedForm.oldValue = newDepartment.ORG + "-" + newDepartment.ACCOUNT

@admin.route('/admin/pendingForms/download', methods=['POST'])
def downloadAllPendingForms():
    currentUser = require_login()

    allPendingForms = FormHistory.select().order_by(-FormHistory.createdDate)
    downloadType = "allPending"
    if currentUser.isLaborAdmin:
        allPendingForms = allPendingForms.where(FormHistory.status.in_(["Pending", "Pre-Student Approval"]))
    elif currentUser.isFinancialAidAdmin or currentUser.isSaasAdmin:
        downloadType = "includeOverloads"
        allPendingForms = allPendingForms.join(OverloadForm).where(FormHistory.status != "Pre-Student Approval", FormHistory.historyType == "Labor Overload Form")
    else:
        abort(403)

    excel = CSVMaker(downloadType, allPendingForms)
    return send_file(excel.relativePath, as_attachment=True, attachment_filename=excel.relativePath.split('/').pop())

@admin.route('/admin/checkedForms', methods=['POST'])
def approved_and_denied_Forms():
    '''
    This function gets the forms that are checked by the user and inserts them into the database
    '''
    try:
        rsp = eval(request.data.decode("utf-8"))
        if rsp:
            approved_details =  modal_approval_and_denial_data(rsp)
            return jsonify(approved_details)
    except Exception as e:
        print(e)
        return jsonify({"Success": False}),500

@admin.route('/admin/updateStatus/<raw_status>', methods=['POST'])
def finalUpdateStatus(raw_status):
    ''' This method changes the status of the pending forms to approved '''
    currentUser = require_login()
    if not currentUser:                    # Not logged in
        return render_template('errors/403.html'), 403
    if not currentUser.isLaborAdmin:       # Not an admin
        return render_template('errors/403.html'), 403

    if raw_status == 'approved':
        new_status = "Approved"
    elif raw_status == 'denied':
        new_status = "Denied"
    else:
        print("Unknown status: ", raw_status)
        return jsonify({"success": False})
    form_ids = eval(request.data.decode("utf-8"))
    return saveStatus(new_status, form_ids, currentUser)

def saveStatus(new_status, form_ids, currentUser):
    try:
        if new_status == 'Denied':
            # Index 1 will always hold the reject reason in the list, so we can
            # set a variable equal to the index value and then slice off the list
            # item before the iteration
            denyReason = form_ids[1]
            form_ids = form_ids[:1]
        for id in form_ids:
            history_type_data = FormHistory.get(FormHistory.formHistoryID == int(id))
            history_type = str(history_type_data.historyType)

            labor_forms = FormHistory.get(FormHistory.formHistoryID == int(id), FormHistory.historyType == history_type)
            labor_forms.status = Status.get(Status.statusName == new_status)
            labor_forms.reviewedDate = date.today()
            labor_forms.reviewedBy = currentUser

            # Add to BANNER
            save_status = True # default true so that we will still save in other cases
            if new_status == 'Approved' and history_type == "Labor Status Form" and labor_forms.formID.POSN_CODE != "S12345": # don't update banner for Adjustment forms or for CS dummy position
                if labor_forms.formID.POSN_CODE == "SNOLAB":
                       labor_forms.formID.weeklyHours = 10
                conn = Banner()
                save_status = conn.insert(labor_forms)

            # if we are able to save
            if save_status:

                if new_status == 'Denied':
                    labor_forms.rejectReason = denyReason
                labor_forms.save()

                email = emailHandler(labor_forms.formHistoryID)
                if new_status == "Denied" and history_type == "Labor Status Form":
                    email.laborStatusFormRejected()
                if new_status == "Approved" and history_type == "Labor Status Form":
                    email.laborStatusFormApproved()
                if new_status == "Approved" and history_type == "Labor Adjustment Form":
                    # This function is triggered whenever an adjustment form is approved.
                    # The following function overrides the original data in lsf with the new data from adjustment form.
                    LSF = LaborStatusForm.get(LaborStatusForm.laborStatusFormID == history_type_data.formID) # getting the specific labor status form
                    overrideOriginalStatusFormOnAdjustmentFormApproval(history_type_data, LSF)

            else:
                print("Unable to update form status for formHistoryID {}.".format(id))
                return jsonify({"success": False}), 500

    except Exception as e:
        print("Error preparing form for status update:", e)
        return jsonify({"success": False}), 500

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


#method extracts data from the data base to papulate pending form approvale modal
def modal_approval_and_denial_data(approval_ids):
    ''' This method grabs the data that populated the on approve modal for lsf'''

    id_list = []
    for formHistoryID in approval_ids:
        formHistory = FormHistory.get(FormHistory.formHistoryID == int(formHistoryID))
        fhistory_id = LaborStatusForm.select().join(FormHistory).where(FormHistory.formHistoryID == int(formHistoryID)).get()
        student_details = LaborStatusForm.get(LaborStatusForm.laborStatusFormID == fhistory_id)
        student_firstname, student_lastname = student_details.studentSupervisee.FIRST_NAME, student_details.studentSupervisee.LAST_NAME
        student_name = str(student_firstname) + " " + str(student_lastname)
        student_pos = student_details.POSN_TITLE
        supervisor_firstname, supervisor_lastname = student_details.supervisor.FIRST_NAME, student_details.supervisor.LAST_NAME
        supervisor_name = str(supervisor_firstname) + " " + str(supervisor_lastname)
        student_hours = student_details.weeklyHours
        student_hours_ch = student_details.contractHours
        student_dept = student_details.department.DEPT_NAME

        if formHistory.adjustedForm:
            if formHistory.adjustedForm.fieldAdjusted == "position":
                position = Tracy().getPositionFromCode(formHistory.adjustedForm.newValue)
                student_pos = position.POSN_TITLE
            if formHistory.adjustedForm.fieldAdjusted == "supervisor":
                supervisor = Supervisor.get(Supervisor.ID == formHistory.adjustedForm.newValue)
                supervisor_firstname, supervisor_lastname = supervisor.FIRST_NAME, supervisor.LAST_NAME
                supervisor_name = str(supervisor_firstname) +" "+ str(supervisor_lastname)
            if formHistory.adjustedForm.fieldAdjusted == "weeklyHours":
                student_hours = formHistory.adjustedForm.newValue
            if formHistory.adjustedForm.fieldAdjusted == "contractHours":
                student_hours_ch = formHistory.adjustedForm.newValue
            if formHistory.adjustedForm.fieldAdjusted == "department":
                department = Department.get(Department.ORG==formHistory.adjustedForm.newValue)
                student_dept = department.DEPT_NAME

        tempList = []
        tempList.append(student_name)
        tempList.append(student_dept)
        tempList.append(student_pos)
        tempList.append(str(student_hours))
        tempList.append(str(student_hours_ch))
        tempList.append(supervisor_name)
        id_list.append(tempList)
    return(id_list)


@admin.route('/admin/getNotes/<formid>', methods=['GET'])
def getNotes(formid):
    '''
    This function retrieves the supervisor and labor department notes.
    '''
    try:
        currentUser = require_login()
        supervisorNotes =  LaborStatusForm.get(LaborStatusForm.laborStatusFormID == formid)
        laborNotes = list(Notes.select().where(Notes.formID == formid))
        laborNotes.reverse()


        notesDict = {}
        if supervisorNotes.supervisorNotes:
            notesDict["supervisorNotes"] = supervisorNotes.supervisorNotes

        # If there are labor office notes, format, and store them in notesDict
        if len(laborNotes) > 0:
            htmlList = []
            for note in laborNotes:
                category = note.noteType[:-5]
                formattedDate = note.date.strftime('%m/%d/%Y')
                htmlList.append(f"<dl class='dl-horizontal text-left'> <b>{formattedDate} |</b> {category} <b>| <i>{note.createdBy.firstName[0]}. {note.createdBy.lastName}</i> | </b>{note.notesContents}</dl>")
            notesDict["laborDepartmentNotes"] = htmlList

        return jsonify(notesDict)

    except Exception as e:
        print("Error on getting notes: ", e)
        return jsonify({"Success": False})

@admin.route('/admin/notesInsert/<formId>', methods=['POST'])
def insertNotes(formId):
    '''
    This function inserts the labor office notes into the database
    '''
    try:
        currentUser = require_login()
        rsp = eval(request.data.decode("utf-8"))
        stripresponse = rsp.strip()
        currentDate = datetime.now().strftime("%Y-%m-%d")  # formats the date to match the peewee format for the database

        if stripresponse:
            Notes.create(formID=formId, createdBy=currentUser, date=currentDate, notesContents=stripresponse, noteType = "Labor Note") # creates a new entry in the laborOfficeNotes table

            return jsonify({"Success": True})

        elif stripresponse=="" or stripresponse==None:
            flash("No changes made to notes.", "danger")
            return jsonify({"Success": False})

    except Exception as e:
        print(e)
        return jsonify({"Success": False}), 500

@admin.route('/admin/overloadModal/<formHistoryID>', methods=['GET'])
def getOverloadModalData(formHistoryID):
    """
    This function will retrieve the data to populate the overload modal.
    """
    try:
        currentUser = require_login()
        departmentStatusInfo = {}
        historyForm = FormHistory.select().where(FormHistory.formHistoryID == int(formHistoryID))
        try:
            financialAidLastEmail = EmailTracker.select().limit(1).where((EmailTracker.recipient == 'Financial Aid') & (EmailTracker.formID == historyForm[0].formID.laborStatusFormID)) .order_by(EmailTracker.date.desc())
            financialAidEmailDate = financialAidLastEmail[0].date.strftime('%m/%d/%y')
        except (AttributeError, IndexError):
            # We expect to see the AttributeError and IndexError if there is no data,
            # and in those cases we set the variables manually
            financialAidEmailDate = 'No Email Sent'

        try:
            SAASLastEmail = EmailTracker.select().limit(1).where((EmailTracker.recipient == 'SAAS') & (EmailTracker.formID == historyForm[0].formID.laborStatusFormID)) .order_by(EmailTracker.date.desc())
            SAASEmailDate = SAASLastEmail[0].date.strftime('%m/%d/%y')
        except (AttributeError, IndexError):
            SAASEmailDate = 'No Email Sent'

        try:
            financialAidStatus = historyForm[0].overloadForm.financialAidApproved.statusName
            FinancialAidApprover = "By " + historyForm[0].overloadForm.financialAidApprover.fullName
        except (AttributeError, IndexError):
            financialAidStatus = None
            FinancialAidApprover = None

        try:
            SAASStatus = historyForm[0].overloadForm.SAASApproved.statusName
            SAASApprover = "By " + historyForm[0].overloadForm.SAASApprover.fullName
        except (AttributeError, IndexError):
            SAASStatus = None
            SAASApprover = None

        try:
            currentPendingForm = FormHistory.select().where((FormHistory.formID == historyForm[0].formID) & ((FormHistory.status == "Pending") | (FormHistory.status == "Pre-Student Approval"))).get()
            if currentPendingForm:
                pendingForm = True
                pendingFormType = currentPendingForm.historyType.historyTypeName
                status = currentPendingForm.status.statusName
        except (AttributeError, IndexError):
            pendingForm = False
            pendingFormType = False

        departmentStatusInfo.update({
                            'SAASStatus': SAASStatus,
                            'SAASEmail': SAASEmailDate,
                            'SAASApprover': SAASApprover,
                            'financialAidStatus': financialAidStatus,
                            'financialAidLastEmail': financialAidEmailDate,
                            'FinancialAidApprover': FinancialAidApprover,
                            })
        noteTotal = Notes.select().where(Notes.formID == historyForm[0].formID.laborStatusFormID).count()
        returnToTab = None
        try:
            returnToTab = globalFormType
        except Exception as e:
            pass
        return render_template('snips/pendingOverloadModal.html',
                                            historyForm = historyForm,
                                            departmentStatusInfo = departmentStatusInfo,
                                            formHistoryID = historyForm[0].formHistoryID,
                                            laborStatusFormID = historyForm[0].formID.laborStatusFormID,
                                            noteTotal = noteTotal,
                                            pendingForm = pendingForm,
                                            pendingFormType = pendingFormType,
                                            formType = returnToTab,
                                            status = status
                                            )
    except Exception as e:
        print("Error Populating Overload Modal:", e)
        return render_template('errors/500.html'), 500

@admin.route('/admin/releaseModal/<formHistoryID>', methods=['GET'])
def getReleaseModalData(formHistoryID):
    """
    This function will retrieve the data to populate the release modal.
    """
    try:
        historyForm = FormHistory.select().where(FormHistory.formHistoryID == int(formHistoryID))
        noteTotal = Notes.select().where(Notes.formID == historyForm[0].formID.laborStatusFormID, Notes.noteType == "Labor Note").count()
        return render_template('snips/pendingReleaseModal.html',
                                            historyForm = historyForm,
                                            formHistoryID = historyForm[0].formHistoryID,
                                            laborStatusFormID = historyForm[0].formID.laborStatusFormID,
                                            noteTotal = noteTotal
                                            )
    except Exception as e:
        print("Error Populating Release Modal:", e)
        return render_template('errors/500.html'), 500

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

def laborAdminOverloadApproval(rsp, historyForm, status, currentUser, currentDate, email):
    if rsp['formType'] == 'Overload':
        overloadForm = OverloadForm.get(OverloadForm.overloadFormID == historyForm.overloadForm.overloadFormID)
        overloadForm.laborApproved = status.statusName
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
                if status.statusName == "Approved Reluctantly":
                    pendingForm.status = "Approved"
                else:
                    pendingForm.status = status.statusName
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
                    if rsp['status'] in ['Approved', 'Approved Reluctantly']:
                        email.laborStatusFormApproved()
                    elif rsp['status'] == 'Denied':
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
        if rsp['status'] in ['Approved', 'Approved Reluctantly']:
            email.LaborOverLoadFormApproved()
        elif rsp['status'] == 'Denied':
            email.LaborOverLoadFormRejected()
    elif rsp['formType'] == 'Release':
        if rsp['status'] == 'Approved':
            email.laborReleaseFormApproved()
        elif rsp['status'] == 'Denied':
            email.laborReleaseFormRejected()
    return jsonify({"Success": True})


@admin.route('/admin/modalFormUpdate', methods=['POST'])
def modalFormUpdate():
    """
    This function will update the overload or release form based on the form
    type and the data from the modal.
    """
    try:
        currentUser = require_login()
        if not currentUser.isLaborAdmin and not (currentUser.isFinancialAidAdmin or currentUser.isSaasAdmin):
            abort(403)
        rsp = eval(request.data.decode("utf-8"))
        if rsp:
            historyForm = FormHistory.get(FormHistory.formHistoryID == rsp['formHistoryID'])
            email = emailHandler(historyForm.formHistoryID)
            currentDate = datetime.now().strftime("%Y-%m-%d")
            status = Status.get(Status.statusName == rsp['status'])

            save_form_status = True

            # send it to banner if they have approved an overload
            if rsp['formType'] == 'Overload' and "Approved" in rsp['status'] and historyForm.formID.POSN_CODE != "S12345":
                conn = Banner()
                save_form_status = conn.insert(historyForm)

            # if we are able to save
            if save_form_status:
                # This try is to handle Overload Forms
                if historyForm.overloadForm:
                    overloadForm = historyForm.overloadForm
                    if currentUser.isLaborAdmin:
                        laborAdminOverloadApproval(rsp, historyForm, status, currentUser, currentDate, email)
                    elif currentUser.isFinancialAidAdmin or currentUser.isSaasAdmin:
                        financialAidSAASOverloadApproval(historyForm, rsp, status, currentUser, currentDate)

                else:
                    # This except is to handle Release Forms
                    historyForm.status = status.statusName
                    historyForm.reviewedDate = currentDate
                    historyForm.reviewedBy = currentUser
                    historyForm.save()
                    if rsp["status"] == "Denied" or "adminNotes" in rsp:
                        newNotes = Notes.create(formID = historyForm.formID,
                                                createdBy = currentUser,
                                                notesContents = "",
                                                noteType = "",
                                                date = currentDate)
                        if rsp["status"] == "Denied":
                            newNotes.notesContents = rsp["denialReason"]
                        elif "adminNotes" in rsp:
                            newNotes.notesContents = rsp["adminNotes"]
                        if currentUser.isFinancialAidAdmin:
                            newNotes.noteType = "Financial Aid Note"
                        elif currentUser.isSaasAdmin:
                            newNotes.noteType = "SAAS Note"
                        elif currentUser.isLaborAdmin:
                            newNotes.noteType = "Supervisor Note"
                        newNotes.save()

                    if rsp["status"] == "Denied":
                        email.laborReleaseFormRejected()
                    elif rsp["status"] == "Approved":
                        email.laborReleaseFormApproved()

            return jsonify({"Success": True})

    except Exception as e:
        print("Error Updating Release/Overload Forms:", e)
        return jsonify({"Success": False}),500

@admin.route('/admin/sendVerificationEmail', methods=['POST'])
def sendEmail():
    """
    This method will send an email to either SAAS, Financial Aid or Student
    """
    try:
        rsp = eval(request.data.decode("utf-8"))
        if rsp:
            historyForm = FormHistory.get_by_id(rsp['formHistoryID'])
            overloadForm = historyForm.overloadForm
            status = Status.get(Status.statusName == 'Pending')
            if rsp['emailRecipient'] == 'studentEmail':
                recipient ="Student"
                email = emailHandler(historyForm.formHistoryID)
                link = makeThirdPartyLink("student", request.host, rsp['formHistoryID'])
                email.LaborOverloadFormStudentReminder(link)

            else:
                if rsp['emailRecipient'] == 'SAASEmail':
                    recipient = 'SAAS'
                    overloadForm.SAASApproved = status.statusName
                    overloadForm.save()
                elif rsp['emailRecipient'] == 'financialAidEmail':
                    recipient = 'Financial Aid'
                    overloadForm.financialAidApproved = status.statusName
                    overloadForm.save()

                email = emailHandler(historyForm.formHistoryID)
                link = makeThirdPartyLink(recipient, request.host, historyForm.formHistoryID)
                email.overloadVerification(recipient, link)
            currentDate = datetime.now().strftime('%m/%d/%y')
            newEmailInformation = {'recipient': recipient,
                                    'emailDate': currentDate,
                                    'status': 'Pending'
                                    }
            return jsonify(newEmailInformation)
    except Exception as e:
        print("Error sending verification email to SASS/Financial Aid:", e)
        return jsonify({"Success": False}),500

@admin.route('/admin/notesCounter', methods=['POST'])
def getNotesCounter():
    """
    This method retrieve the number of notes a labor status form has
    """
    try:
        rsp = eval(request.data.decode("utf-8"))
        if rsp:
            noteTotal = Notes.select().where(Notes.formID == rsp['laborStatusFormID'], Notes.noteType == "Labor Note").count()
            noteDictionary = {'noteTotal': noteTotal}
            return jsonify(noteDictionary)
    except Exception as e:
        print("Error selecting admin notes:", e)
        return jsonify({"Success": False}),500
