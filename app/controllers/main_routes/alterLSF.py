from datetime import date, datetime
from flask import json, jsonify, request, flash
from app.controllers.main_routes import *
from app.controllers.main_routes.main_routes import *
from app.controllers.main_routes.laborHistory import *
from app.models.formHistory import FormHistory
from app.models.user import User
from app.models.supervisor import Supervisor
from app.logic.userInsertFunctions import createSupervisorFromTracy
from app.logic.emailHandler import *
from app.login_manager import require_login
from app.logic.tracy import Tracy, InvalidQueryException
from app.models.notes import Notes
from app.models.supervisor import Supervisor
from app.login_manager import require_login
from app.logic.alterLSF import modifyLSF, adjustLSF


@main_bp.route("/alterLSF/<laborStatusKey>", methods=["GET"])
def alterLSF(laborStatusKey):
    """
    This function gets all the form's data and populates the front end
    """
    currentUser = require_login()
    if not currentUser:        # Not logged in
        return render_template("errors/403.html")
    if not currentUser.isLaborAdmin:       # Not an admin
        if currentUser.student and not currentUser.supervisor: # If a student is logged in and trying to get to this URL then send them back to their own page.
            return redirect("/laborHistory/" + currentUser.student.ID)

    currentDate = date.today()
    #If logged in....
    #Step 1: get form attached to the student (via labor history modal)
    form = LaborStatusForm.get(LaborStatusForm.laborStatusFormID == laborStatusKey)
    # If todays date is greater than the adjustment cut off date on the term and the form is an adjustment LSF,
    # then we do not want to give users access to the adjustment page

    # Query the status of the form to determine if correction or adjust LSF
    formStatus = (FormHistory.get(FormHistory.formID == laborStatusKey).status_id)

    if currentDate > form.termCode.adjustmentCutOff and formStatus == "Approved" and not currentUser.isLaborAdmin:
        return render_template("errors/403.html")
    #Step 2: get prefill data from said form, then the data that populates dropdowns for supervisors and position
    prefillstudent = form.studentSupervisee.FIRST_NAME + " "+ form.studentSupervisee.LAST_NAME+" ("+form.studentSupervisee.ID+")"
    prefillsupervisor = form.supervisor.FIRST_NAME +" "+ form.supervisor.LAST_NAME
    prefillsupervisorPIDM = form.supervisor.PIDM
    superviser_id = form.supervisor.ID
    prefilldepartment = form.department.ORG
    prefilldepartmentaccount = form.department.ACCOUNT
    prefillposition = form
    prefilljobtype = form.jobType
    prefillterm = form.termCode
    prefillstartdate = form.startDate
    prefillenddate = form.endDate
    totalHours = 0
    if form.weeklyHours != None:
        prefillhours = form.weeklyHours
        allTermForms = LaborStatusForm.select().join_from(LaborStatusForm, Student).where((LaborStatusForm.termCode == form.termCode) & (LaborStatusForm.laborStatusFormID != laborStatusKey) & (LaborStatusForm.studentSupervisee.ID == form.studentSupervisee.ID))
        if allTermForms:
            for i in allTermForms:
                totalHours += i.weeklyHours
    else:
        prefillhours = form.contractHours

    #These are the data fields to populate our dropdowns(Supervisor. Position)
    supervisors = Tracy().getSupervisors()
    positions = Tracy().getPositionsFromDepartment(form.department.ORG, form.department.ACCOUNT)
    departments = Tracy().getDepartments()

    # supervisors from the old system WILL have a Supervisor record, but might not have a Tracy record
    oldSupervisor = Supervisor.get_or_none(ID = form.supervisor.ID)
    if not oldSupervisor:
        try:
            oldSupervisor = Tracy().getSupervisorFromID(form.supervisor.ID)
        except InvalidQueryException:
            print("The bnumber {} was not found in Supervisor or Tracy", form.supervisor.ID)
            oldSupervisor = {'ID': form.supervisor.ID}

    notes = Notes.select().where(Notes.formID == laborStatusKey, Notes.noteType == "Supervisor Note") # Gets labor department notes from the laborofficenotes table

    return render_template( "main/alterLSF.html",
				            title=("Adjust Labor Status Form" if formStatus == "Approved" else "Labor Status Correction Form"),
                            username = currentUser,
                            superviser_id = superviser_id,
                            prefillstudent = prefillstudent,
                            prefillsupervisor = prefillsupervisor,
                            prefillsupervisorPIDM = prefillsupervisorPIDM,
                            prefilldepartment = prefilldepartment,
                            prefilldepartmentaccount = prefilldepartmentaccount,
                            prefillposition = prefillposition,
                            prefilljobtype = prefilljobtype,
                            prefillterm = prefillterm,
                            prefillstartdate = prefillstartdate,
                            prefillenddate = prefillenddate,
                            prefillhours = prefillhours,
                            supervisors = supervisors,
                            positions = positions,
                            departments=departments,
                            form = form,
                            oldSupervisor = oldSupervisor,
                            totalHours = totalHours,
                            currentUser = currentUser,
                            notes = notes
                          )

@main_bp.route("/alterLSF/getDate/<termcode>", methods=['GET'])
def getDate(termcode):
    """ Get the start and end dates of the selected term. """
    dates = Term.select().where(Term.termCode == termcode)
    datesDict = {}
    for date in dates:
        start = date.termStart
        end  = date.termEnd
        primaryCutOff = date.primaryCutOff
        if primaryCutOff is None:
            datesDict[date.termCode] = {"Start Date":datetime.strftime(start, "%m/%d/%Y")  , "End Date": datetime.strftime(end, "%m/%d/%Y")}
        else:
            datesDict[date.termCode] = {"Start Date":datetime.strftime(start, "%m/%d/%Y")  , "End Date": datetime.strftime(end, "%m/%d/%Y"), "Primary Cut Off": datetime.strftime(primaryCutOff, "%m/%d/%Y"), "isBreak": date.isBreak, "isSummer": date.isSummer}
    return json.dumps(datesDict)

@main_bp.route("/alterLSF/fetchPositions/<departmentOrg>/<departmentAccount>", methods=['GET'])
def fetchPositions(departmentOrg, departmentAccount):
    currentUser = require_login()
    positions = Tracy().getPositionsFromDepartment(departmentOrg, departmentAccount)
    positionDict = {}
    for position in positions:
        if position.POSN_CODE != "S12345" or currentUser.isLaborAdmin:
            positionDict[position.POSN_CODE] = {"POSN_TITLE": position.POSN_TITLE, "WLS": position.WLS, "POSN_CODE": position.POSN_CODE}
    return json.dumps(positionDict)

@main_bp.route("/alterLSF/submitAlteredLSF/<laborStatusKey>", methods=["POST"])
def submitAlteredLSF(laborStatusKey):
    """
    Submits an altered LSF form and creates a formHistory entry if appropriate
    """
    try:
        currentUser = require_login()
        if not currentUser:        # Not logged in
            return render_template("errors/403.html")
        currentDate = datetime.now().strftime("%Y-%m-%d")
        fieldsChanged = eval(request.data.decode("utf-8")) # This fixes byte indices must be intergers or slices error
        fieldsChanged = dict(fieldsChanged)
        student = LaborStatusForm.get(LaborStatusForm.laborStatusFormID == laborStatusKey)
        formStatus = (FormHistory.get(FormHistory.formID == laborStatusKey).status_id)
        formHistoryIDs = []
        lsf = LaborStatusForm.get(LaborStatusForm.laborStatusFormID == laborStatusKey)
        for fieldName in fieldsChanged:
            if formStatus =="Pending" or formStatus == "Pre-Student Approval":
                modifyLSF(fieldsChanged, fieldName, lsf, currentUser, host=request.host)
            elif formStatus =="Approved":
                changedForm = adjustLSF(fieldsChanged, fieldName, lsf, currentUser, host=request.host)
                if changedForm:
                    formHistoryIDs.append(changedForm)
        if formStatus == "Approved":
            for formHistory in formHistoryIDs:
                try:
                    email = emailHandler(formHistory)
                    if "supervisor" in fieldsChanged:
                        email.laborStatusFormAdjusted(fieldsChanged["supervisor"]["newValue"])
                    else:
                        email.laborStatusFormAdjusted()
                except Exception as e:
                    print("An error occured while attempting to send adjustment form emails: ", e)
                message = "Your labor adjustment form(s) for {0} {1} have been submitted.".format(student.studentSupervisee.FIRST_NAME, student.studentSupervisee.LAST_NAME)
        else:
            message = "Your labor status form for {0} {1} has been modified.".format(student.studentSupervisee.FIRST_NAME, student.studentSupervisee.LAST_NAME)
        flash(message, "success")
        return jsonify({"Success": True})

    except Exception as e:
        message = "An error occured. Your labor {0} form(s) for {1} {2} were not submitted.".format("status" if formStatus == "Pending" else "adjustment",
                                                                                                    student.studentSupervisee.FIRST_NAME,
                                                                                                    student.studentSupervisee.LAST_NAME)
        flash(message, "danger")
        print("An error occured during form submission:", e)
        return jsonify({"Success": False}), 500


