from flask import render_template , flash, redirect, url_for, request, g, jsonify, current_app, send_file
from flask_login import current_user, login_required
from app.controllers.main_routes import *
from app.models.user import *
from app.models.laborStatusForm import *
from app.models.formHistory import *
from app.models.overloadForm import *
from app.models.department import *
from app.models.student import *
from app.controllers.errors_routes.handlers import *
from app.login_manager import require_login
from flask import json
from flask import make_response
import datetime
import re
from app import cfg
from app.controllers.main_routes.download import CSVMaker
from fpdf import FPDF
from app.logic.buttonStatus import ButtonStatus
from app.logic.tracy import Tracy
from app.models.supervisor import Supervisor
from app.models.department import Department
from app.models.studentLaborEvaluation import StudentLaborEvaluation
from app.models.formHistory import FormHistory
from app.logic.tracy import Tracy
from app.logic.userInsertFunctions import getOrCreateStudentRecord

@main_bp.route('/laborHistory/<id>', methods=['GET'])
@main_bp.route('/laborHistory/<departmentName>/<id>', methods=['GET'])
def laborhistory(id, departmentName = None):
    try:
        currentUser = require_login()
        if not currentUser:
            print("Not currentuser")                # Not logged in
            return render_template('errors/403.html'), 403
        student = getOrCreateStudentRecord(bnumber=id)
        studentForms = FormHistory.select().join_from(FormHistory, LaborStatusForm).join_from(FormHistory, HistoryType).where(FormHistory.formID.studentSupervisee == student,
        FormHistory.historyType.historyTypeName == "Labor Status Form").order_by(FormHistory.formID.startDate.desc())
        authorizedForms = set(studentForms)
        if not currentUser.isLaborAdmin:
            # View only your own form history
            if currentUser.student and not currentUser.supervisor:
                if currentUser.student.ID != id:
                    return redirect('/laborHistory/' + currentUser.student.ID)
            elif currentUser.supervisor and not currentUser.student:
                supervisorForms = FormHistory.select() \
                                  .join_from(FormHistory, LaborStatusForm) \
                                  .where((FormHistory.formID.supervisor == currentUser.supervisor.ID) | (FormHistory.createdBy == currentUser)) \
                                  .distinct()
                deptForms = FormHistory.select() \
                                  .join(LaborStatusForm) \
                                  .join( Department) \
                                  .where(FormHistory.formID.department.DEPT_NAME == currentUser.supervisor.DEPT_NAME) \
                                  .distinct()
                authorizedForms = set(studentForms).intersection(set(supervisorForms).union(set(deptForms)))


                if len(authorizedForms) == 0:
                    print("len wrong?")
                    return render_template('errors/403.html'), 403
        authorizedForms = sorted(authorizedForms,key=lambda f:f.reviewedDate if f.reviewedDate else f.createdDate, reverse=True)
        laborStatusFormList = ','.join([str(form.formID.laborStatusFormID) for form in studentForms])
        return render_template( 'main/formHistory.html',
    				            title=('Labor History'),
                                student = student,
                                username=currentUser.username,
                                laborStatusFormList = laborStatusFormList,
                                authorizedForms = authorizedForms,
                                departmentName = departmentName
                              )

    except Exception as e:
        print("Error Loading Student Labor History", e)
        return render_template('errors/500.html'), 500

@main_bp.route("/laborHistory/download" , methods=['POST'])
def downloadFormHistory():
    """
    This function is called when the download button is pressed.  It runs a function for writing to an excel sheet that is in download.py.
    This function downloads the created excel sheet of the history from the page.
    """
    try:
        data = request.form
        historyList = data["listOfForms"].split(',')
        excel = CSVMaker("studentHistory", historyList, includeEvals = True)
        return send_file(excel.relativePath, mimetype='text/csv', as_attachment=True, attachment_filename=excel.relativePath.split('/').pop())
    except:
        return render_template('errors/500.html'), 500

@main_bp.route('/laborHistory/modal/<statusKey>', methods=['GET'])
def populateModal(statusKey):
    """
    This function creates the modal and populates it with the history of a selected position.  It works with the openModal() function in laborhistory.js
    to create the modal, and append all of the data gathered here form the database to the modal.  It also sets a button state which decides which buttons
    to put on the modal depending on what form is in the history.
    """
    try:
        currentUser = require_login()
        if not currentUser:                    # Not logged in
            return render_template('errors/403.html'), 403
        forms = FormHistory.select().where(FormHistory.formID == statusKey).order_by(FormHistory.createdDate.desc(), FormHistory.formHistoryID.desc())
        statusForm = LaborStatusForm.get(LaborStatusForm.laborStatusFormID == statusKey)
        student = Student.get(Student.ID == statusForm.studentSupervisee)
        currentDate = datetime.date.today()
        pendingformType = None
        first = True  # temp variable to determine if this is the newest form
        for form in forms:
            if first:
                buttonState = ButtonStatus()
                buttonState.set_button_states(form, currentUser)
                first = not first
            if form.adjustedForm != None:  # If a form has been adjusted then we want to retrieve supervisors names using the new and old values stored in adjusted table
                newValue = form.adjustedForm.newValue
                oldValue = form.adjustedForm.oldValue
                if form.adjustedForm.fieldAdjusted == "supervisor": # if supervisor field in adjust forms has been changed,
                    newSupervisor = Supervisor.get(Supervisor.ID == newValue)
                    oldSupervisor = Supervisor.get(Supervisor.ID == oldValue)
                    # we are temporarily storing the supervisor name in new value,
                    # because we want to show the supervisor name in the hmtl template.
                    form.adjustedForm.oldValue = oldSupervisor.FIRST_NAME + " " + oldSupervisor.LAST_NAME # old supervisor name
                    form.adjustedForm.newValue = newSupervisor.FIRST_NAME +" "+ newSupervisor.LAST_NAME

                if form.adjustedForm.fieldAdjusted == "position": # if position field has been changed in adjust form then retriev position name.
                    newPosition = Tracy().getPositionFromCode(newValue)
                    oldPosition = Tracy().getPositionFromCode(oldValue)
                    # temporarily storing the new position name in new value, and old position name in old value
                    # because we want to show these information in the hmtl template.
                    form.adjustedForm.newValue = newPosition.POSN_TITLE + " (" + newPosition.WLS+")"
                    form.adjustedForm.oldValue = oldPosition.POSN_TITLE + " (" + oldPosition.WLS+")"

                if form.adjustedForm.fieldAdjusted == "department":
                    newDepartment = Department.get(Department.ORG == newValue)
                    oldDepartment = Department.get(Department.ORG == oldValue)
                    form.adjustedForm.newValue = newDepartment.DEPT_NAME
                    form.adjustedForm.oldValue = oldDepartment.DEPT_NAME
                # Converts the field adjusted value out of camelcase into a more readable format to be displayed on the front end
                form.adjustedForm.fieldAdjusted = re.sub(r"(\w)([A-Z])", r"\1 \2", form.adjustedForm.fieldAdjusted).title()

            # Pending release or adjustment forms need the historyType known
            if (form.releaseForm != None or form.adjustedForm != None) and form.status.statusName == "Pending":
                pendingformType = form.historyType.historyTypeName

        resp = make_response(render_template('snips/studentHistoryModal.html',
                                            forms = forms,
                                            currentUser = currentUser,
                                            statusForm = statusForm,
                                            currentDate = currentDate,
                                            pendingformType = pendingformType,
                                            buttonState = buttonState
                                            ))
        return (resp)
    except Exception as e:
        print("Error on button state: ", e)
        message = "An error occured. Contact support using the link at the bottom of the website."
        flash(message, "danger")
        return (jsonify({"Success": False}))

@main_bp.route('/laborHistory/modal/printPdf/<statusKey>', methods=['GET'])
def ConvertToPDF(statusKey):
    """
    This function returns
    """
    try:
        forms = FormHistory.select().where(FormHistory.formID == statusKey).order_by(FormHistory.createdDate.desc())
        statusForm = LaborStatusForm.select().where(LaborStatusForm.laborStatusFormID == statusKey)
        pdf = make_response(render_template('main/pdfTemplate.html',
                        forms = forms,
                        statusForm = statusForm
                        ))
        return (pdf)
    except Exception as e:
        return(jsonify({"Success": False}))


@main_bp.route('/laborHistory/modal/withdrawform', methods=['POST'])
def withdraw_form():
    """
    This function deletes forms from the database when they are pending and the "withdraw" button is clicked.
    """
    try:
        currentUser = require_login()
        if not currentUser:                    # Not logged in
            return render_template('errors/403.html'), 403
        rsp = eval(request.data.decode("utf-8"))
        student = LaborStatusForm.get(rsp["FormID"])
        studentID = student.studentSupervisee.ID
        selectedPendingForms = FormHistory.select().join(Status).where(FormHistory.formID == rsp["FormID"]).where(FormHistory.status.statusName == "Pending" | FormHistory.status.statusName == "Pre-Student Approval").order_by(FormHistory.historyType.asc())
        for form in selectedPendingForms:
            if form.historyType.historyTypeName == "Labor Status Form":
                historyFormToDelete = FormHistory.get(FormHistory.formHistoryID == form.formHistoryID)
                laborStatusFormToDelete = LaborStatusForm.get(LaborStatusForm.laborStatusFormID == form.formID.laborStatusFormID)
                historyFormToDelete.delete_instance()
                laborStatusFormToDelete.delete_instance()
            elif form.historyType.historyTypeName == "Labor Overload Form":
                historyFormToDelete = FormHistory.get(FormHistory.formHistoryID == form.formHistoryID)
                overloadFormToDelete = OverloadForm.get(OverloadForm.overloadFormID == form.overloadForm.overloadFormID)
                overloadFormToDelete.delete_instance()
                historyFormToDelete.delete_instance()
        message = "Your selected form for {0} {1} has been withdrawn.".format(student.studentSupervisee.FIRST_NAME, student.studentSupervisee.LAST_NAME)
        flash(message, "success")

        if currentUser.student:
            return jsonify({"Success":True, "url":"/laborHistory/" + studentID})
        else:

            return jsonify({"Success":True, "url":"/"})
    except Exception as e:
        print(e)
        message = "An error occured. Your selected form for {0} {1} was not withdrawn.".format(student.studentSupervisee.FIRST_NAME, student.studentSupervisee.LAST_NAME)
        flash(message, "danger")
        return jsonify({"Success": False, "url":"/"})
