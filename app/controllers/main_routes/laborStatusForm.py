from flask_login import login_required
from app.controllers.main_routes import *
from app.login_manager import require_login
from app.models.user import *
from app.models.status import *
from app.models.laborStatusForm import *
from app.models.overloadForm import *
from app.models.formHistory import *
from app.models.historyType import *
from app.models.term import *
from app.models.student import Student
from app.models.department import *
from flask import json, jsonify
from flask import request
from datetime import datetime, date, timedelta
from flask import Flask, redirect, url_for, flash
from app import cfg
from app.logic.emailHandler import*
from app.logic.userInsertFunctions import*
from app.models.supervisor import Supervisor
from app.logic.tracy import Tracy
from app.controllers.main_routes.laborReleaseForm import createLaborReleaseForm
from app.controllers.admin_routes.allPendingForms import saveStatus

@main_bp.route('/laborstatusform', methods=['GET'])
@main_bp.route('/laborstatusform/<laborStatusKey>', methods=['GET'])
def laborStatusForm(laborStatusKey = None):
    """ Render labor Status Form, and pre-populate LaborStatusForm page with the correct information when redirected from Labor History."""
    currentUser = require_login()
    if not currentUser:        # Not logged in
        return render_template('errors/403.html'), 403
    if not currentUser.isLaborAdmin:
        if currentUser.student and not currentUser.supervisor:
            return redirect('/laborHistory/' + currentUser.student.ID)

    # Logged in
    supervisorForms = ((FormHistory.select().where((FormHistory.historyType == "Labor Status Form") & (FormHistory.formID.termCode.termState) & ((FormHistory.formID.supervisor == currentUser.supervisor) | (FormHistory.createdBy == currentUser)))
                                            .join(LaborStatusForm)
                                            .join(Term)).distinct()).order_by(FormHistory.createdDate.desc())
    for form in supervisorForms:
        print(form.formID.laborStatusFormID)
    students = Tracy().getStudents()
    terms = Term.select().where(Term.termState == "open") # changed to term state, open, closed, inactive
    staffs = Tracy().getSupervisors()
    departments = Tracy().getDepartments()

    # Only prepopulate form if current user is the supervisor or creator of the form.
    if laborStatusKey != None:
        selectedLSForm = LaborStatusForm.get(LaborStatusForm.laborStatusFormID == laborStatusKey)
        selectedFormHistory = FormHistory.get(FormHistory.formID == laborStatusKey)
        creator = selectedFormHistory.createdBy.supervisor.ID
        supervisor = selectedLSForm.supervisor.ID
        if currentUser.supervisor.ID == supervisor or currentUser.supervisor.ID == creator or currentUser.isLaborAdmin:
            forms = LaborStatusForm.get(LaborStatusForm.laborStatusFormID == laborStatusKey) # getting labor status form id, to prepopulate laborStatusForm.
        else:
            forms = None
    else:
        forms = None
    return render_template( 'main/laborStatusForm.html',
				            title=('Labor Status Form'),
                            UserID = currentUser,
                            forms = forms,
                            students = students,
                            supervisorForms = supervisorForms,
                            terms = terms,
                            staffs = staffs,
                            departments = departments)

@main_bp.route('/laborstatusform/userInsert', methods=['POST'])
def userInsert():
    """ Create labor status form. Create labor history form. Most of the functions called here are in userInsertFunctions.py"""
    currentUser = require_login()
    if not currentUser:        # Not logged in
        return render_template('errors/403.html'), 403
    rsp = (request.data).decode("utf-8")  # This turns byte data into a string
    rspFunctional = json.loads(rsp)
    all_forms = []
    for i in range(len(rspFunctional)):

        # Get a student record for the given bnumber
        try:
            student = getOrCreateStudentRecord(bnumber=rspFunctional[i]['stuBNumber'])
            supervisor = createSupervisorFromTracy(bnumber=rspFunctional[i]['stuSupervisorID'])
        except InvalidUserException as e:
            print(e)
            return "", 500

        department, created = Department.get_or_create(DEPT_NAME = rspFunctional[i]['stuDepartment'])
        term, created = Term.get_or_create(termCode = rspFunctional[i]['stuTermCode'])
        try:
            lsf = createLaborStatusForm(student.ID, supervisor.ID, department.departmentID, term, rspFunctional[i])
            createOverloadFormAndFormHistory(rspFunctional[i], lsf, currentUser, host=request.host)
            try:
                emailDuringBreak(checkForSecondLSFBreak(term.termCode, student.ID), term)
            except Exception as e:
                print("Error when sending emails during break: " + str(e))

            all_forms.append(True)
        except Exception as e:
            all_forms.append(False)
            print("ERROR on creating Labor Status Form/Overload Form" + str(e))

    flash("Form(s) submitted successfully! They will be eligible for approval in one business day.", "success")
    return jsonify(all_forms)

@main_bp.route("/laborstatusform/getDate/<termcode>", methods=['GET'])
def getDates(termcode):
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

@main_bp.route("/laborstatusform/getPositions/<departmentOrg>/<departmentAcct>", methods=['GET'])
def getPositions(departmentOrg, departmentAcct):
    """ Get all of the positions that are in the selected department """
    currentUser = require_login()
    positions = Tracy().getPositionsFromDepartment(departmentOrg,departmentAcct)
    positionDict = {}
    for position in positions:
        if position.POSN_CODE != "S12345" or currentUser.isLaborAdmin:
            positionDict[position.POSN_CODE] = {"position": position.POSN_TITLE, "WLS":position.WLS, "positionCode":position.POSN_CODE}
    return json.dumps(positionDict)

@main_bp.route("/laborstatusform/getstudents/<termCode>/<student>", methods=["POST"])
@main_bp.route("/laborstatusform/getstudents/<termCode>/<student>/<isOneLSF>", methods=["GET"])
def checkForPrimaryOrSecondLSFBreak(termCode, student, isOneLSF=None):
    currentUser = require_login()
    if isOneLSF:
        return checkForSecondLSFBreak(termCode, student)
    else:
        return checkForPrimaryPosition(termCode, student, currentUser)

@main_bp.route("/laborstatusform/getcompliance/<department>", methods=["GET"])
def checkCompliance(department):
    """ Gets the compliance status of a department. """
    depts = Department.select().where(Department.ORG == department)
    deptDict = {}
    for dept in depts:
        deptDict['Department'] = {'Department Compliance': dept.departmentCompliance}
    return json.dumps(deptDict)

@main_bp.route("/laborstatusform/checktotalhours/<termCode>/<student>/<hours>", methods=["GET"])
def checkTotalHours(termCode, student, hours):
    """ Counts the total number of hours for the student after the new lsf is filled. """
    shortCode, spring, fall, ayTermCode = termCode[-2:], '12', '11', None
    if shortCode == spring or shortCode == fall: # Count the AY hours only for Fall and Spring, not break terms.
        ayTermCode = termCode[:-2] + '00'
    positions = FormHistory.select()\
                           .join_from(FormHistory, LaborStatusForm)\
                           .where(((FormHistory.formID.termCode == termCode) | (FormHistory.formID.termCode == ayTermCode)),
                                  FormHistory.formID.studentSupervisee == student,
                                  FormHistory.historyType == "Labor Status Form",
                                  ((FormHistory.status == "Approved") | (FormHistory.status == "Approved Reluctantly") | (FormHistory.status == "Pending"))
                                  )
    term = Term.get(Term.termCode == termCode)
    totalHours = 0
    for item in positions:
        formID = item.formID
        releasedForm = FormHistory.select().where(FormHistory.formID == formID, FormHistory.historyType == "Labor Release Form", FormHistory.status == "Approved")
        if not releasedForm:
            if term.isBreak:
                totalHours = totalHours + item.formID.contractHours
            else:
                totalHours = totalHours + item.formID.weeklyHours
    totalHours = totalHours + int(hours)
    return json.dumps(totalHours)

@main_bp.route("/laborStatusForm/modal/releaseAndRehire", methods=['POST'])
def releaseAndRehire():
    try:
        currentUser = require_login()
        null=None; true = True; false= False
        studentDict = eval(request.data.decode("utf-8"))
        previousPrimaryPosition = FormHistory.select()\
                                             .join_from(FormHistory, LaborStatusForm)\
                                             .where(FormHistory.formID.termCode == studentDict["stuTermCode"], FormHistory.formID.studentSupervisee == studentDict["stuBNumber"], FormHistory.historyType == "Labor Status Form", FormHistory.formID.jobType == "Primary")\
                                             .order_by(FormHistory.formHistoryID.desc())\
                                             .get()
        # Release previous labor status form
        todayDate = date.today()
        tomorrowDate = datetime.now()+timedelta(1)
        createLaborReleaseForm(currentUser, previousPrimaryPosition.formID, tomorrowDate, "Satisfactory", "Released by labor admin.", "Approved", todayDate, currentUser)

        # Create new labor status form
        student = getOrCreateStudentRecord(bnumber=studentDict['stuBNumber'])
        supervisor = createSupervisorFromTracy(bnumber=studentDict['stuSupervisorID'])
        department, created = Department.get_or_create(DEPT_NAME = studentDict['stuDepartment'])
        term, created = Term.get_or_create(termCode = studentDict['stuTermCode'])

        newLaborStatusForm = createLaborStatusForm(student.ID, supervisor.ID, department.departmentID, term, studentDict)
        formHistory = createOverloadFormAndFormHistory(studentDict, newLaborStatusForm, currentUser, host=request.host)

        # Mark the newly created labor status form as approved in both our system and Banner
        saveStatus("Approved", [str(formHistory.formHistoryID)], currentUser)

        flash("Form has been successfully released and submitted.", "success")
        return jsonify({"Success":True})
    except Exception as e:
        print("Error on release and rehire: ", e)
        return jsonify({"Success": False})
