from datetime import date, datetime
from playhouse.shortcuts import model_to_dict
from flask import json, jsonify, request, redirect, url_for, abort, flash, g

from app.controllers.main_routes import *
from app.logic.emailHandler import*
from app.logic.utils import makeThirdPartyLink
from app.login_manager import require_login
from app.models import mainDB
from app.models.supervisor import Supervisor
from app.models.user import *
from app.models.laborStatusForm import *
from app.models.student import *
from app.models.formHistory import *
from app.models.overloadForm import *

@main_bp.route('/studentOverloadApp/<formHistoryId>', methods=['GET'])
def studentOverloadApp(formHistoryId):
    currentUser = require_login()
    overloadForm = FormHistory.get_by_id(formHistoryId)
    if not currentUser.isLaborAdmin:
        if not currentUser:        # Not logged in
            return render_template('errors/403.html'), 403
        if not currentUser.student:
            return render_template('errors/403.html'), 403
        if currentUser.student.ID != overloadForm.formID.studentSupervisee.ID:
            return render_template('errors/403.html'), 403
    lsfForm = (LaborStatusForm.select(LaborStatusForm, Student, Term, Department)
                    .join(Student, attr="studentSupervisee").switch()
                    .join(Term).switch()
                    .join(Department)
                    .where(LaborStatusForm.laborStatusFormID == overloadForm.formID)).get()
    prefillStudentName = lsfForm.studentSupervisee.FIRST_NAME + " "+ lsfForm.studentSupervisee.LAST_NAME
    prefillStudentBnum = lsfForm.studentSupervisee.ID
    prefillStudentCPO = lsfForm.studentSupervisee.STU_CPO
    prefillStudentClass = lsfForm.studentSupervisee.CLASS_LEVEL
    prefillTerm = lsfForm.termCode.termName
    prefillDepartment = lsfForm.department.DEPT_NAME
    prefillPosition = lsfForm.POSN_TITLE
    prefillHoursOverload = lsfForm.weeklyHours

    listOfTerms = []
    today = date.today()
    termYear = today.year * 100
    termsInYear = Term.select(Term).where(Term.termCode.between(termYear-1, termYear + 15))
    TermsNeeded=[]
    for term in termsInYear:
        if not term.isBreak:
            TermsNeeded.append(term.termCode)

    studentSecondaryLabor = (LaborStatusForm.select(LaborStatusForm.laborStatusFormID)
                                .where( LaborStatusForm.studentSupervisee_id == prefillStudentBnum,
                                        LaborStatusForm.jobType == "Secondary",
                                        LaborStatusForm.termCode.in_(TermsNeeded)))

    studentPrimaryLabor = (LaborStatusForm.select(LaborStatusForm.laborStatusFormID)
                                .where( LaborStatusForm.studentSupervisee_id == prefillStudentBnum,
                                        LaborStatusForm.jobType == "Primary",
                                        LaborStatusForm.termCode.in_(TermsNeeded)))
    formIDPrimary = []
    for primaryForm in studentPrimaryLabor:
        studentPrimaryHistory = (FormHistory.select().where(
                                    FormHistory.formID == primaryForm,
                                    FormHistory.historyType == "Labor Status Form",
                                    FormHistory.status.in_(["Approved","Pending","Pre-Student Approval"]) ))
        formIDPrimary.append(studentPrimaryHistory)
    formIDSecondary = []

    for secondaryForm in studentSecondaryLabor:
        studentSecondaryHistory = (FormHistory.select().where(
                                    FormHistory.formID == secondaryForm,
                                    FormHistory.historyType == "Labor Status Form",
                                    FormHistory.status.in_(["Approved","Pending","Pre-Student Approval"]) ))
        formIDSecondary.append(studentSecondaryHistory)

    totalCurrentHours = 0
    for i in formIDPrimary:
        for j in i:
            if str(j.status) == "Approved":
                totalCurrentHours += j.formID.weeklyHours
    for i in formIDSecondary:
        for j in i:
            if str(j.status) == "Approved":
                totalCurrentHours += j.formID.weeklyHours
    totalFormHours = totalCurrentHours + prefillHoursOverload

    return render_template( 'main/studentOverloadApp.html',
				            title=('student Overload Application'),
                            username = currentUser,
                            overloadForm = overloadForm,
                            prefillStudentName = prefillStudentName,
                            prefillStudentBnum = prefillStudentBnum,
                            prefillStudentCPO = prefillStudentCPO,
                            prefillStudentClass = prefillStudentClass,
                            prefillTerm = prefillTerm,
                            prefillDepartment = prefillDepartment,
                            prefillPosition = prefillPosition,
                            prefillHoursOverload = prefillHoursOverload,
                            currentPrimary = formIDPrimary,
                            currentSecondary = formIDSecondary,
                            totalCurrentHours = totalCurrentHours,
                            totalFormHours = totalFormHours,
                            isAdjustment = False,
                            adjustmentForm = None 
                          )

@main_bp.route('/studentAdjustmentApp/<formHistoryId>', methods=['GET'])
def studentAdjustmentApp(formHistoryId):
    currentUser = require_login()
    AdjustmentForm = FormHistory.get_by_id(formHistoryId)
    if not currentUser.isLaborAdmin:
        if not currentUser:        # Not logged in
            return render_template('errors/403.html'), 403
        if not currentUser.student:
            return render_template('errors/403.html'), 403
        
        if currentUser.student.ID != AdjustmentForm.formID.studentSupervisee.ID:
            return render_template('errors/403.html'), 403
    lsfForm = (LaborStatusForm.select(LaborStatusForm, Student, Term, Department)
                    .join(Student, attr="studentSupervisee").switch()
                    .join(Term).switch()
                    .join(Department)
                    .where(LaborStatusForm.laborStatusFormID == AdjustmentForm.formID)).get()
    prefillStudentName = lsfForm.studentSupervisee.FIRST_NAME + " "+ lsfForm.studentSupervisee.LAST_NAME
    prefillStudentBnum = lsfForm.studentSupervisee.ID
    prefillStudentCPO = lsfForm.studentSupervisee.STU_CPO
    prefillStudentClass = lsfForm.studentSupervisee.CLASS_LEVEL
    prefillTerm = lsfForm.termCode.termName
    prefillDepartment = lsfForm.department.DEPT_NAME
    prefillPosition = lsfForm.POSN_TITLE
    prefillHoursOverload = lsfForm.weeklyHours

   
    today = date.today()
    termYear = today.year * 100
    termsInYear = Term.select(Term).where(Term.termCode.between(termYear-1, termYear + 15))
    TermsNeeded=[]
    for term in termsInYear:
        if not term.isBreak:
            TermsNeeded.append(term.termCode)

    studentSecondaryLabor = (LaborStatusForm.select(LaborStatusForm.laborStatusFormID)
                                .where( LaborStatusForm.studentSupervisee_id == prefillStudentBnum,
                                        LaborStatusForm.jobType == "Secondary",
                                        LaborStatusForm.termCode.in_(TermsNeeded)))

    studentPrimaryLabor = (LaborStatusForm.select(LaborStatusForm.laborStatusFormID)
                                .where( LaborStatusForm.studentSupervisee_id == prefillStudentBnum,
                                        LaborStatusForm.jobType == "Primary",
                                        LaborStatusForm.termCode.in_(TermsNeeded)))
    formIDPrimary = []
    for primaryForm in studentPrimaryLabor:
        studentPrimaryHistory = (FormHistory.select().where(
                                    FormHistory.formID == primaryForm,
                                    FormHistory.historyType == "Labor Status Form",
                                    FormHistory.status.in_(["Approved","Pending","Pre-Student Approval"]) ))
        formIDPrimary.append(studentPrimaryHistory)
    formIDSecondary = []

    for secondaryForm in studentSecondaryLabor:
        studentSecondaryHistory = (FormHistory.select().where(
                                    FormHistory.formID == secondaryForm,
                                    FormHistory.historyType == "Labor Status Form",
                                    FormHistory.status.in_(["Approved","Pending","Pre-Student Approval"]) ))
        formIDSecondary.append(studentSecondaryHistory)

    totalCurrentHours = 0
    for i in formIDPrimary:
        for j in i:
            if str(j.status) == "Approved":
                totalCurrentHours += j.formID.weeklyHours
    for i in formIDSecondary:
        for j in i:
            if str(j.status) == "Approved":
                totalCurrentHours += j.formID.weeklyHours
    totalFormHours = totalCurrentHours + prefillHoursOverload


    # Access the related AdjustedForm record directly
    adjusted_change = AdjustmentForm.adjustedForm  
    print("testign adjustment")
    print(adjusted_change)

    field_name = adjusted_change.fieldAdjusted
    old_value  = adjusted_change.oldValue
    new_value  = adjusted_change.newValue

    print("old=", old_value)


    return render_template( 'main/studentOverloadApp.html',
				            title=('student Adjustment Application'),
                            username = currentUser,
                            AdjustmentForm = AdjustmentForm,
                            adjusted_change = adjusted_change,
                            field_name = field_name,
                            old_value = old_value,
                            new_value = new_value,
                            prefillStudentName = prefillStudentName,
                            prefillStudentBnum = prefillStudentBnum,
                            prefillStudentCPO = prefillStudentCPO,
                            prefillStudentClass = prefillStudentClass,
                            prefillTerm = prefillTerm,
                            prefillDepartment = prefillDepartment,
                            prefillPosition = prefillPosition,
                            prefillHoursOverload = prefillHoursOverload,
                            currentPrimary = formIDPrimary,
                            currentSecondary = formIDSecondary,
                            totalCurrentHours = totalCurrentHours,
                            totalFormHours = totalFormHours,
                            isAdjustment = True,
                            overloadForm = None
                          )
        


@main_bp.route('/studentOverloadApp/withdraw/<formHistoryId>', methods=['POST'])
def withdrawRequest(formHistoryId):
    formHistory = FormHistory.get_by_id(formHistoryId)
    if formHistory.historyType_id != "Labor Overload Form":
        ("Somehow we reached a non-overload form history entry ({formHistoryId}) from studentOverloadApp.")
        abort(500)

    # send a withdrawal notification to student and supervisor
    email = emailHandler(formHistory.formHistoryID)
    email.LaborOverloadFormWithdrawn()

    # TODO should we email financial aid?

    formHistory.overloadForm.delete_instance()
    formHistory.formID.delete_instance()
    #formHistory.delete_instance()

    flash("Overload Request Withdrawn", "success")
    return redirect("/")

@main_bp.route('/studentOverloadApp/update/<overloadFormHistoryID>', methods=['POST'])
def updateDatabase(overloadFormHistoryID):
    try:
        overloadReason = request.form.get('overloadReason')
        if not overloadReason:
            abort(500)

        oldStatus = Status.get(Status.statusName == "Pre-Student Approval")
        newStatus = Status.get(Status.statusName == "Pending")

        overloadFormHistory = FormHistory.get(FormHistory.formHistoryID == overloadFormHistoryID)
        originalFormHistory = (FormHistory.select()
                                           .where(FormHistory.formID == overloadFormHistory.formID)
                                           .where(FormHistory.status == oldStatus)
                                           .where(FormHistory.historyType_id == "Labor Status Form")).get()

        with mainDB.atomic() as transaction:
            # Update statuses
            overloadFormHistory.status = newStatus
            overloadFormHistory.save()
            originalFormHistory.status = newStatus
            originalFormHistory.save()

            # Update base student confirmation
            originalFormHistory.formID.studentResponseDate = datetime.now()
            originalFormHistory.formID.studentConfirmation = True
            originalFormHistory.formID.save()

            # Update overload form
            overloadForm = overloadFormHistory.overloadForm
            overloadForm.studentOverloadReason = overloadReason
            overloadForm.save()

            email = emailHandler(overloadFormHistory.formHistoryID)
            link = makeThirdPartyLink("Financial Aid", request.host, overloadFormHistory.formHistoryID)
            email.overloadVerification("Financial Aid", link)

        flash("Overload Request Submitted", "success")
        return g.currentUser.student.ID

    except Exception as e:
        ("ERROR: " + str(e))
        abort(500)
