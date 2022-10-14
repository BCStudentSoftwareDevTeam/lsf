from app.controllers.admin_routes import admin
from app.models.user import *
from app.login_manager import require_login
from app.models.laborStatusForm import *
from datetime import date
from app.models.formHistory import *
from flask import json, jsonify
from flask import request, render_template, flash
from app.models.overloadForm import *
from app import cfg
from app.models.notes import Notes
from datetime import datetime, date
from app.models.status import *
from app.logic.emailHandler import*

@admin.route('/admin/financialAidOverloadApproval/<formHistoryID>', methods=['GET'])
@admin.route('/admin/saasOverloadApproval/<formHistoryID>', methods=['GET'])
def financialAidOverload(formHistoryID):
    '''
    This function prefills all the information for a student's current job and overload request.
    '''
    currentUser = require_login() # we need to check to see if the person logged in is SAAS or FinancialAid

    if not currentUser: # Not logged in
        return render_template('errors/403.html'), 403
    if not (currentUser.isFinancialAidAdmin or currentUser.isSaasAdmin): # Not an admin
        return render_template('errors/403.html'), 403

    overloadFormHistory = FormHistory.get(FormHistory.formHistoryID == formHistoryID)
    lsfForm = overloadFormHistory.formID # get the labor status form that is tied to the overload form

    ###-------- Get Current Position Information -------###
    # Get all labor status forms for the same student in the same term and see if they have a primary position.
    # IF YES: populate the "Current Position" Fields with the information from that labor status form.
    allLaborStatusForms = (LaborStatusForm.select()
                                .join(FormHistory)
                                .where(FormHistory.status_id.in_(["Approved", "Approved Reluctantly", "Pending"]),
                                       FormHistory.historyType_id == "Labor Status Form",
                                       LaborStatusForm.studentSupervisee == lsfForm.studentSupervisee.ID, 
                                       LaborStatusForm.termCode == lsfForm.termCode))
    totalHours = {"secondaryHours" : 0, "primaryHours": 0}
    supervisor = department = ""
    primaryForm = {}
    for form in allLaborStatusForms:
        if form.jobType == "Primary":
            primaryForm = form
            supervisor = form.supervisor.FIRST_NAME +" "+ form.supervisor.LAST_NAME
            department = form.department.DEPT_NAME
            totalHours["primaryHours"] = form.weeklyHours
        if form.jobType == "Secondary":
            totalHours["secondaryHours"] += form.weeklyHours

    contractDate = "{} - {}".format(lsfForm.startDate.strftime('%m/%d/%Y'), lsfForm.endDate.strftime('%m/%d/%Y'))
    userDept = "Financial Aid"
    if currentUser.isSaasAdmin:
        userDept = "SAAS"

# will need to add term to the interface and then have a prefill variable
    return render_template( 'admin/financialAidOverload.html',
                        overloadFormHistory = overloadFormHistory,
                        lsfForm = lsfForm,
                        primaryForm = primaryForm,
                        userDept = userDept,
                        department = department,
                        supervisor= supervisor,
                        contractDate = contractDate,
                        totalOverloadHours = totalHours["primaryHours"] + totalHours["secondaryHours"]
                      )

@admin.route("/admin/financialAidOverloadApproval/<status>", methods=["POST"])
@admin.route('/admin/saasOverloadApproval/<status>', methods=['POST'])
def formApproval(status):
    ''' This function will get the status (Approved/Denied) and make the appropriate
    changes in the database for that specific overload form'''
    try:
        currentUser = require_login() #we need to check to see if the person logged in is SAAS or FinancialAid
        if not currentUser: # Not logged in
            return render_template('errors/403.html'), 403
        if not (currentUser.isFinancialAidAdmin or currentUser.isSaasAdmin): # Not an admin
            return render_template('errors/403.html'), 403
        if status == "denied":
            newStatus = "Denied"
        elif status == "approved":
            newStatus = "Approved"
        else:
            return jsonify({'error': 'Unknown Status'}), 500

        rsp = eval(request.data.decode("utf-8"))
        currentDate = datetime.now().strftime("%Y-%m-%d")
        selectedFormHistory = FormHistory.get(FormHistory.formHistoryID == rsp["formHistoryID"])
        selectedOverload = OverloadForm.get(OverloadForm.overloadFormID == selectedFormHistory.overloadForm.overloadFormID)
        formStatus = Status.get(Status.statusName == newStatus)
        if currentUser.isFinancialAidAdmin:
            typeOfNote = "Financial Aid Note"
        else:
            typeOfNote = "SAAS Note"

        if rsp:
            ## New Entry in AdminNote Table
            newNoteEntry = Notes.create(formID=selectedFormHistory.formID.laborStatusFormID,
                                        createdBy=currentUser,
                                        date=currentDate,
                                        notesContents=rsp["denialNote"],
                                        noteType = typeOfNote)
            ## Updating the overloadform Table
            if currentUser.isFinancialAidAdmin:
                selectedOverload.financialAidApproved = formStatus.statusName
                selectedOverload.financialAidApprover = currentUser
                selectedOverload.financialAidReviewDate = currentDate
            if currentUser.isSaasAdmin:
                selectedOverload.SAASApproved = formStatus.statusName
                selectedOverload.SAASApprover = currentUser
                selectedOverload.SAASReviewDate = currentDate
            selectedOverload.save()
        # email = emailHandler(rsp["formHistoryID"]) ## sending email to Labor Admin on any submission
        # email.verifiedOverloadNotification()
        return jsonify({'success':True}), 200

    except Exception as e:
        print("Unable to Deny the OverloadForm",type(e).__name__ + ":", e)
        return jsonify({'error': "Unable to Deny the form"}), 500
