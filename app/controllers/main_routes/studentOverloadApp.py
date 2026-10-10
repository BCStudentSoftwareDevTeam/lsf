from datetime import date, datetime
from app.models import overloadForm
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
    #  always load the clicked history entry
    currentHistory = FormHistory.get_by_id(formHistoryId)

    # STEP 2 — find the real FormHistory row that holds the overloadForm (reason)
    overloadReasonHistory = (
        FormHistory
        .select()
        .where(
            (FormHistory.formID == currentHistory.formID) &
            (FormHistory.overloadForm.is_null(False))
        )
        .order_by(FormHistory.createdDate.desc())
        .first()
    )

    # STEP 3 — use whichever record has the overloadForm, fallback to clicked one
    if overloadReasonHistory:
        overloadHistory = overloadReasonHistory
    else:
        overloadHistory = currentHistory
    if not currentUser.isLaborAdmin:
        if not currentUser:        # Not logged in
            return render_template('errors/403.html'), 403
        if not currentUser.student:
            return render_template('errors/403.html'), 403
        if currentUser.student.ID != overloadHistory.formID.studentSupervisee.ID:
            return render_template('errors/403.html'), 403
    lsfForm = (LaborStatusForm.select(LaborStatusForm, Student, Term, Department)
                    .join(Student, attr="studentSupervisee").switch()
                    .join(Term).switch()
                    .join(Department)
                    .where(LaborStatusForm.laborStatusFormID == overloadHistory.formID)).get()
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

    adjustedField, oldValue, newValue = (None, None, None)

    if overloadHistory.adjustedForm:    
        adjustmentForm = overloadHistory.adjustedForm

        adjustedField = adjustmentForm.fieldAdjusted
        oldValue  = adjustmentForm.oldValue
        newValue  = adjustmentForm.newValue

        if adjustedField == "department":
            oldValue = Department.get(Department.ORG == oldValue).DEPT_NAME
            newValue = Department.get(Department.ORG == newValue).DEPT_NAME
    return render_template( 'main/studentOverloadApp.html',
				            title=('student Overload Application'),
                            username = currentUser,
                            overloadHistory = overloadHistory,
                            adjustedField = adjustedField,
                            oldValue = oldValue,
                            newValue = newValue,
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
                          )

        
@main_bp.route('/studentOverloadApp/withdraw/<formHistoryId>', methods=['POST'])
def withdrawRequest(formHistoryId):
    formHistory = FormHistory.get_by_id(formHistoryId)
    if formHistory.historyType_id != "Labor Adjustment Form":
        abort(500)
    # send a withdrawal notification to student and supervisor
    email = emailHandler(formHistory.formHistoryID)
    email.LaborOverloadFormWithdrawn()
    # TODO should we email financial aid?
    formHistory.adjustedForm.delete_instance()
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

        # if status is pending that means we have an adjustment 
        # if status is "pre-student then it means we have an overload"     
        newStatus = Status.get(Status.statusName == "Pending")
        overloadFormHistory = FormHistory.get(FormHistory.formHistoryID == overloadFormHistoryID)
        originalFormHistory = (
            FormHistory
            .select()
            .where(FormHistory.formID == overloadFormHistory.formID.laborStatusFormID)
            .where((FormHistory.status == "Pre-Student Approval") | (FormHistory.status == "Approved"))
            .where(FormHistory.historyType_id.in_([
                     "Labor Status Form",
                     "Labor Overload Form",
                     "Labor Adjustment Form",
                 ]))
            .first())
        overloadHistoryType, _ = HistoryType.get_or_create(
            historyTypeName="Labor Overload Form"
        )
        with mainDB.atomic() as transaction:
            overloadForm = OverloadForm.create(studentOverloadReason=request.form.get("studentOverloadReason"))
            if overloadFormHistory:
                overloadFormHistory.overloadForm = overloadForm
                overloadFormHistory.save()
            else:
                overloadFormHistory = FormHistory.create(
                    formID=originalFormHistory.formID,
                    historyType=overloadHistoryType,
                    overloadForm=overloadForm,
                    createdBy=g.currentUser,
                    createdDate=datetime.now().date(),
                    status=newStatus,
                )
            overloadFormHistory.status = newStatus
            overloadFormHistory.save()
            originalFormHistory.status = newStatus
            originalFormHistory.save()

            originalFormHistory.formID.studentResponseDate = datetime.now()
            originalFormHistory.formID.studentConfirmation = True
            originalFormHistory.formID.save()
            overloadForm = overloadFormHistory.overloadForm  # should now be non-None
            overloadForm.studentOverloadReason = overloadReason
            overloadForm.save()  # only needed if modified after create
            email = emailHandler(overloadFormHistory.formHistoryID)
            link = makeThirdPartyLink("Financial Aid", request.host, overloadFormHistory.formHistoryID)
            email.overloadVerification("Financial Aid", link)

        flash("Overload Request Submitted", "success")
        if g.currentUser.student:
            return jsonify({"bnumber": g.currentUser.student.ID}), 200
        return jsonify({"bnumber": None}), 200
    except Exception as e:
        print("ERROR: " + str(e))
        abort(500)
