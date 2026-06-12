from datetime import datetime, date
from flask import abort, flash, jsonify, redirect, send_file, make_response, g
import json
from peewee import JOIN

from app.models import mainDB
from app.login_manager import *
from app.controllers.admin_routes import admin
from app.controllers.errors_routes.handlers import *
from app.models.laborReleaseForm import LaborReleaseForm
from app.models.laborStatusForm import LaborStatusForm
from app.models.adjustedForm import AdjustedForm
from app.models.emailTracker import EmailTracker
from app.models.overloadForm import OverloadForm
from app.models.notes import Notes
from app.logic.emailHandler import emailHandler
from app.logic.utils import makeThirdPartyLink, calculateExpirationDate
from app.models.formHistory import FormHistory
from app.models.term import Term
from app.logic.banner import Banner
from app.logic.tracy import Tracy
from app.models.Tracy.stuposn import STUPOSN
from app.models.supervisor import Supervisor
from app.models.student import Student
from app.models.historyType import HistoryType
from app.models.department import Department
from app.models.status import Status
from app.logic.allPendingForms import saveStatus, laborAdminOverloadApproval, financialAidSAASOverloadApproval, modal_approval_and_denial_data, checkAdjustment
from app.logic.download import CSVMaker, saveFormSearchResult, retrieveFormSearchResult

@admin.route('/admin/pendingForms/<formType>',  methods=['GET'])
def allPendingForms(formType):
    try:
        currentUser = require_login()
        if not currentUser:                    # Not logged in
            return render_template('errors/403.html'), 403      
    
        if not (currentUser.isLaborAdmin or currentUser.isLaborDepartmentStudent):       # Not an admin
            if currentUser.student: # logged in as a student
                return redirect('/laborHistory/' + currentUser.student.ID)
            elif currentUser.supervisor and not currentUser.isFinancialAidAdmin and not currentUser.isSaasAdmin:
                return render_template('errors/403.html'), 403
        formList = None
        historyType = None
        pageTitle = ""
        approvalTarget = ""
        completedOverloadFormCounter = 0
        laborStatusFormCounter = FormHistory.select().where((FormHistory.status == "Pending") & (FormHistory.historyType == 'Labor Status Form')).count()
        adjustedFormCounter = FormHistory.select().where((FormHistory.status == 'Pending') & (FormHistory.historyType == 'Labor Adjustment Form')).count()
        releaseFormCounter = FormHistory.select().where((FormHistory.status == 'Pending') & (FormHistory.historyType == 'Labor Release Form')).count()
        preStudentApprovalCounter = FormHistory.select().where(FormHistory.status == 'Pre-Student Approval',FormHistory.historyType == 'Labor Status Form',FormHistory.overloadForm.is_null()).count()

        if currentUser.isLaborAdmin or currentUser.isLaborDepartmentStudent:
            overloadFormCounter = FormHistory.select().where(FormHistory.status.in_(('Pending','Pre-Student Approval')) & (FormHistory.historyType == 'Labor Overload Form')).count()
        elif currentUser.isFinancialAidAdmin:
            overloadFormCounter = FormHistory.select().join_from(FormHistory, OverloadForm)\
                                             .where((FormHistory.status == 'Pending') & (FormHistory.historyType == 'Labor Overload Form'))\
                                             .where((FormHistory.overloadForm.financialAidApproved == 'Pending') | (FormHistory.overloadForm.financialAidApproved == None)).count()

            completedOverloadFormCounter = FormHistory.select().join_from(FormHistory, OverloadForm)\
                                                     .where(FormHistory.historyType == 'Labor Overload Form')\
                                                     .where((FormHistory.overloadForm.financialAidApproved == 'Approved') | (FormHistory.overloadForm.financialAidApproved == 'Denied by Admin')).count()
        elif currentUser.isSaasAdmin:
            overloadFormCounter = FormHistory.select().join_from(FormHistory, OverloadForm)\
                                             .where((FormHistory.status == 'Pending') & (FormHistory.historyType == 'Labor Overload Form'))\
                                             .where((FormHistory.overloadForm.SAASApproved == 'Pending') | (FormHistory.overloadForm.SAASApproved == None)).count()

            completedOverloadFormCounter = FormHistory.select().join_from(FormHistory, OverloadForm)\
                                                     .where(FormHistory.historyType == 'Labor Overload Form')\
                                                     .where((FormHistory.overloadForm.SAASApproved == 'Approved') | (FormHistory.overloadForm.SAASApproved == 'Denied by Admin')).count()

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

        elif formType == "preStudentApproval":
            historyType = "Labor Status Form"
            approvalTarget = ""
            pageTitle = "Pre-Student Approval"
            


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
                                      .where((FormHistory.overloadForm.financialAidApproved == 'Approved') | (FormHistory.overloadForm.financialAidApproved == 'Denied by Admin'))
                                      )

        if currentUser.isSaasAdmin:
            if formType == "pendingOverload":
                baseQuery = (baseQuery.where(FormHistory.status == 'Pending')
                                      .where(FormHistory.historyType == "Labor Overload Form")
                                      .where((FormHistory.overloadForm.SAASApproved == 'Pending') | (FormHistory.overloadForm.SAASApproved == None)))
            elif formType == "completedOverload":
                baseQuery = (baseQuery.where(FormHistory.historyType == "Labor Overload Form")
                                      .where((FormHistory.overloadForm.SAASApproved == 'Approved') | (FormHistory.overloadForm.SAASApproved == 'Denied by Admin')))

        if currentUser.isLaborAdmin or currentUser.isLaborDepartmentStudent:
            if formType == "pendingOverload":
                baseQuery = baseQuery.where(FormHistory.status.in_(('Pending','Pre-Student Approval')),FormHistory.historyType == "Labor Overload Form")
            elif formType == "preStudentApproval":
                baseQuery = baseQuery.where(FormHistory.status == "Pre-Student Approval", FormHistory.historyType == historyType, FormHistory.overloadForm.is_null())
            elif formType in ("pendingLabor","pendingAdjustment","pendingRelease"):
                baseQuery = baseQuery.where(FormHistory.status == "Pending", FormHistory.historyType == historyType)

        formList = baseQuery.order_by(-FormHistory.createdDate).distinct()

        # store forms in database for later download
        downloadId = saveFormSearchResult(pageTitle, formList, formType)

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
        result = make_response(render_template(
            'admin/allPendingForms.html',
            title=pageTitle,
            username=currentUser.username,
            pageTitle=pageTitle,
            formList = formList,
            formType= formType,
            modalTarget = approvalTarget,
            overloadFormCounter = overloadFormCounter,
            laborStatusFormCounter = laborStatusFormCounter,
            adjustedFormCounter  = adjustedFormCounter,
            releaseFormCounter = releaseFormCounter,
            preStudentApprovalCounter = preStudentApprovalCounter,
            completedOverloadFormCounter = completedOverloadFormCounter,
            pendingOverloadFormPairs = pendingOverloadFormPairs,
            downloadId = downloadId
        ))
        return result
    
    
    except Exception as e:
        print("Error Loading all Pending Forms:", e)
        return render_template('errors/500.html'), 500


@admin.route('/admin/pendingForms/download', methods=['POST'])
def downloadAllPendingForms():
    searchResult = retrieveFormSearchResult(request.form.get('downloadId'))
    if not searchResult:
        print(f"[ERROR] Missing or invalid download id was provided by the user.")
        abort(500)

    formHistoryIds = json.loads(searchResult.formHistoryIds)
    formHistories = FormHistory.select().where(FormHistory.formHistoryID.in_(formHistoryIds)).order_by(-FormHistory.createdDate)

    additionalSpreadsheetFields = []
    if g.currentUser.isFinancialAidAdmin or g.currentUser.isSaasAdmin:
        additionalSpreadsheetFields.append("overloads")
    elif not currentUser.isLaborAdmin or currentUser.isLaborDepartmentStudent:
        abort(403)
    
    excel = CSVMaker(
        searchResult.name, 
        requestedLSFs = formHistories, 
        additionalSpreadsheetFields=additionalSpreadsheetFields
    )

    return send_file(excel.relativePath, as_attachment=True, download_name=excel.relativePath.split('/').pop())

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

@admin.route('/admin/skipStudentApproval', methods=['POST'])
def skipStudentApproval():
    '''
    Mark a form as approved by the student and update status to pending
    '''
    if not (g.currentUser.isLaborAdmin or g.currentUser.isLaborDepartmentStudent):
        abort(403)

    note = "Skipped Student Approval: " + request.form.get("skipNote")
    formID = request.form.get("formID")

    # TODO should pull this out into a function in a logic file after PR #494 is merged

    # Update form history status
    try:
        form = LaborStatusForm.get_by_id(formID)
    except DoesNotExist:
        flash("Invalid form ID provided", "danger")
        abort(404)

    # make sure our database changes happen all at once
    try:
        with mainDB.atomic():
            form.studentConfirmation = True
            form.studentResponseDate = date.today()
            form.save()

            # Get the form history record. XXX Currently restricted to original lsf.
            formHistory = FormHistory.get_or_none(FormHistory.formID == form.laborStatusFormID, 
                                                  FormHistory.historyType == "Labor Status Form")
            if formHistory:
                formHistory.status = "Pending"
                formHistory.save()

            # Add Labor note
            Notes.create(formID=form.laborStatusFormID, createdBy=g.currentUser, date=date.today(), notesContents=note, noteType = "Labor Note")

    except Exception as e:
        print("Error skipping student approval", e)
        flash("Error skipping student approval. Please try again.","danger")

    return redirect('/admin/pendingForms/preStudentApproval')

@admin.route('/admin/resendStudentConfirmation/<formID>', methods=['POST'])
def resendStudentConfirmation(formID):
    if not (g.currentUser.isLaborAdmin or g.currentUser.isLaborDepartmentStudent):       # Not an admin
        return render_template('errors/403.html'), 403

    try:
        # get the base form history for the given labor status form
        formhistory = FormHistory.get(FormHistory.formID == formID, FormHistory.historyType == "Labor Status Form")

        # make a new expiration date
        formhistory.formID.studentExpirationDate = calculateExpirationDate()
        formhistory.formID.save()

        # resend but only to students
        emailer = emailHandler(formhistory.formHistoryID)
        if formhistory.formID.termCode.isBreak:
            emailer.checkRecipient("Break Labor Status Form Submitted For Student")
        else:
            emailer.checkRecipient("Labor Status Form Submitted For Student")

        return jsonify({"student_email":formhistory.formID.studentSupervisee.STU_EMAIL});

    except Exception as e:
        print("Error sending confirmation email. Invalid Form ID.", e)
        flash("Error sending confirmation email. Please try again.","danger")
        abort(500)



@admin.route('/admin/updateStatus/<raw_status>', methods=['POST'])
def finalUpdateStatus(raw_status):
    ''' This method changes the status of the pending forms '''
    currentUser = require_login()
    if not currentUser:                    # Not logged in
        return render_template('errors/403.html'), 403
    if not currentUser.isLaborAdmin or currentUser.isLaborDepartmentStudent:       # Not an admin
        return render_template('errors/403.html'), 403

    if raw_status == 'approved':
        new_status = "Approved"
    elif raw_status == 'denied':
        new_status = "Denied by Admin"
    elif raw_status == 'pending':
        new_status = "Pending"
    else:
        print("Unknown status: ", raw_status)
        return jsonify({"success": False})

    flash("Forms have been successfully updated.", "success")
    form_ids = eval(request.data.decode("utf-8"))
    return saveStatus(new_status, form_ids, currentUser)

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
            if currentUser.isLaborAdmin or currentUser.isLaborDepartmentStudent:
                Notes.create(formID=formId, createdBy=currentUser, date=currentDate, notesContents=stripresponse, noteType = "Labor Note") # creates a new entry in the laborOfficeNotes table
            elif currentUser.isFinancialAidAdmin:
                Notes.create(formID=formId, createdBy=currentUser, date=currentDate, notesContents=stripresponse, noteType = "Financial Aid Note")
            elif currentUser.isSaasAdmin:
                Notes.create(formID=formId, createdBy=currentUser, date=currentDate, notesContents=stripresponse, noteType = "SAAS Note")
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
        studentLinks = {}
        for form in historyForm:
            studentLinks[form.formHistoryID] = makeThirdPartyLink("student", request.host, form.formHistoryID)
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
        return render_template('snips/pendingOverloadModal.html',
                                            historyForm = historyForm,
                                            departmentStatusInfo = departmentStatusInfo,
                                            formHistoryID = historyForm[0].formHistoryID,
                                            laborStatusFormID = historyForm[0].formID.laborStatusFormID,
                                            noteTotal = noteTotal,
                                            pendingForm = pendingForm,
                                            pendingFormType = pendingFormType,
                                            formType = returnToTab,
                                            status = status,
                                            studentLinks = studentLinks
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

@admin.route('/admin/modalFormUpdate', methods=['POST'])
def modalFormUpdate():
    """
    This function will update the overload or release form based on the form
    type and the data from the modal.
    """
    try:
        currentUser = require_login()
        if not (currentUser.isLaborAdmin or currentUser.isLaborDepartmentStudent) and not (currentUser.isFinancialAidAdmin or currentUser.isSaasAdmin):
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
                    if currentUser.isLaborAdmin or currentUser.isLaborDepartmentStudent:
                        laborAdminOverloadApproval(rsp, historyForm, status, currentUser, currentDate, email)
                    elif currentUser.isFinancialAidAdmin or currentUser.isSaasAdmin:
                        financialAidSAASOverloadApproval(historyForm, rsp, status, currentUser, currentDate)

                else:
                    # This except is to handle Release Forms
                    historyForm.status = status.statusName
                    historyForm.reviewedDate = currentDate
                    historyForm.reviewedBy = currentUser
                    historyForm.save()
                    if rsp["status"] == "Denied by Admin" or "adminNotes" in rsp:
                        newNotes = Notes.create(formID = historyForm.formID,
                                                createdBy = currentUser,
                                                notesContents = "",
                                                noteType = "",
                                                date = currentDate)
                        if rsp["status"] == "Denied by Admin":
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

                    if rsp["status"] == "Denied by Admin":
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
            noteTotal = Notes.select().where(Notes.formID == rsp['laborStatusFormID']).count()
            noteDictionary = {'noteTotal': noteTotal}
            return jsonify(noteDictionary)
    except Exception as e:
        print("Error selecting admin notes:", e)
        return jsonify({"Success": False}),500
