from flask import flash, send_file
from peewee import prefetch
from playhouse.shortcuts import model_to_dict
from app.controllers.main_routes import *
from app.controllers.main_routes.download import CSVMaker
from app.login_manager import *
from app.models.laborStatusForm import LaborStatusForm
from app.models.department import Department
from app.models.term import Term
from app.models.historyType import HistoryType
from app.models.formHistory import FormHistory
from datetime import datetime, date
from flask import request, redirect
from flask import json, jsonify
from flask import make_response
from app.logic.tracy import Tracy
from app.logic.tracy import InvalidQueryException
import app.login_manager as login_manager
import base64
import time
import sys

currentlyEnrolledBNumbers = []

# Check if a student is currently a student at Berea. Only get the list from Tracy once
# This means we'll need to restart the application to refresh tracy data (currently a nightly restart)
def isCurrentStudent(bnumber):
    global currentlyEnrolledBNumbers

    if not currentlyEnrolledBNumbers:
        currentlyEnrolledBNumbers = [s.ID.strip() for s in Tracy().getStudents()]

    return (bnumber in currentlyEnrolledBNumbers)

@main_bp.before_app_request
def before_request():
    pass # TODO Do we need to do anything here? User stuff?

@main_bp.route('/logout', methods=['GET'])
def logout():
    return redirect(login_manager.logout())

@main_bp.route('/', methods=['GET', 'POST'])
@main_bp.route('/main/students', methods=['GET', 'POST'])
@main_bp.route('/main/department', methods=['GET', 'POST'])
@main_bp.route('/main/department/<department>', methods=['GET', 'POST'])
def index(department = None):
    try:
        currentUser = require_login()
        if not currentUser:
            return render_template('errors/403.html'), 403
        if not currentUser.isLaborAdmin:
            if currentUser.student and not currentUser.supervisor:   # logged in as a student
                return redirect('/laborHistory/' + currentUser.student.ID)
            if currentUser.supervisor:       # logged in as a Supervisor
                # Checks all the forms where the current user has been the creator or the supervisor, and grabs all the departments associated with those forms. Will only grab each department once.
                departments = FormHistory.select(FormHistory.formID.department.DEPT_NAME) \
                                .join_from(FormHistory, LaborStatusForm) \
                                .join_from(LaborStatusForm, Department) \
                                .where((FormHistory.formID.supervisor == currentUser.supervisor.ID) | (FormHistory.createdBy == currentUser)) \
                                .order_by(FormHistory.formID.department.DEPT_NAME.asc()) \
                                .distinct()
        elif currentUser.isLaborAdmin:   # logged in as an admin
            # Grabs every single department that currently has at least one labor status form in it
            # FIXME: Why not grab departments from the departments table?
            departments = FormHistory.select(FormHistory.formID.department.DEPT_NAME) \
                            .join_from(FormHistory, LaborStatusForm) \
                            .join_from(LaborStatusForm, Department) \
                            .order_by(FormHistory.formID.department.DEPT_NAME.asc()) \
                            .distinct()

        todayDate = date.today()

        activeTerms = Term.select(Term.termName).where(Term.termStart <= todayDate, Term.termEnd >= todayDate).order_by(Term.termEnd.desc())
        tableTabs = ["Pending"] + [str(at.termName) for at in activeTerms] + ["Past"]

        # Grabs all the labor status forms where the current user is the supervisor
        if currentUser.supervisor:
            formsBySupervisees = (FormHistory.select()
                                             .join_from(FormHistory, LaborStatusForm)
                                             .join_from(FormHistory, HistoryType)
                                             .where(FormHistory.formID.supervisor == currentUser.supervisor.ID,
                                                    FormHistory.historyType.historyTypeName == "Labor Status Form")
                                             .order_by(FormHistory.formID.startDate.desc()))

        pastSupervisees = formsBySupervisees.select().where(FormHistory.formID.endDate < todayDate)

        # On the click of the download button, 'POST' method will send all checked boxes from modal to excel maker
        if request.method == 'POST':
            value =[]
            # The "Try" and "Except" block here is needed because if the user tries to use the download button before they chose
            # a department from the Department dropdown, it will throw a NameError. The reason behind the error is because the vairbales
            # "currentDepartmentStudents", "allDepartmentStudents", and "inactiveDepStudent" are empty until the user chooses a department, so
            # trying to iterate through the empty variables causes the error. The "Try" and "Except" blocks will catch this error so that
            # a user can use the download button before they chose a department.
            try:
                for form in currentDepartmentStudents:
                    name = str(form.formID.laborStatusFormID)
                    if request.form.get(name):
                        value.append(request.form.get(name))
                for form in allDepartmentStudents:
                    name = str(form.formID.laborStatusFormID)
                    if request.form.get(name):
                        value.append(request.form.get(name))
                for form in inactiveDepStudent:
                    name = str(form.formID.laborStatusFormID)
                    if request.form.get(name):
                        value.append(request.form.get(name))
            except NameError as e:
                print("The runtime error happens because a department has not yet been selected.")
            for form in currentSupervisees:
                name = str(form.formID.laborStatusFormID)
                if request.form.get(name):
                    value.append( request.form.get(name))
            for form in pastSupervisees:
                name = str(form.formID.laborStatusFormID)
                if request.form.get(name):
                    value.append( request.form.get(name))
            for form in inactiveSupervisees:
                name = str(form.formID.laborStatusFormID)
                if request.form.get(name):
                    value.append( request.form.get(name))


            # Prevents 'POST' method from sending the same value twice to excel maker

            excel = CSVMaker("studentList", value, includeEvals = True)
            # Returns the file path so the button will download the file
            return send_file(excel.relativePath,as_attachment=True, attachment_filename=excel.relativePath.split('/').pop())

        return render_template( 'main/index.html',
                				    title=('Home'),
                                    currentSupervisees = formsBySupervisees,
                                    pastSupervisees = pastSupervisees,
                                    UserID = currentUser,
                                    currentUserDepartments = departments,
                                    tableTabs = tableTabs
                              )
    except Exception as e:
        #TODO We have to return some sort of error page
        print('Error in Supervisor Portal:', e)
        return "",500

@main_bp.route('/main/department/selection/<departmentSelected>', methods=['GET'])
def populateDepartment(departmentSelected):
    # try:
    currentUser = require_login()
    todayDate = date.today()

    try:
        department = Department.get(Department.DEPT_NAME == departmentSelected)
    except DoesNotExist:
        print("Department '{}' does not exist".format(departmentSelected))
        return jsonify({"Success": False})

    deptPositions = [p.POSN_CODE for p in Tracy().getPositionsFromDepartment(department.ORG, department.ACCOUNT)]

    # This will retrieve all the forms that are tied to the department the user selected from the select picker
    currentFormsByDept = prefetch(FormHistory.select()
                              .join_from(FormHistory, LaborStatusForm)
                              .join_from(FormHistory, HistoryType)
                              .where((FormHistory.historyType.historyTypeName == "Labor Status Form") & (FormHistory.formID.POSN_CODE << deptPositions) & (FormHistory.formID.endDate >= todayDate))
                              .order_by(FormHistory.formID.endDate.desc()), LaborStatusForm.select().where(LaborStatusForm.POSN_CODE << deptPositions))
    pastFormsByDept = prefetch(FormHistory.select()
                              .join_from(FormHistory, LaborStatusForm)
                              .join_from(FormHistory, HistoryType)
                              .where((FormHistory.historyType.historyTypeName == "Labor Status Form") & (FormHistory.formID.POSN_CODE << deptPositions) & (FormHistory.formID.endDate < todayDate))
                              .order_by(FormHistory.formID.endDate.desc()), LaborStatusForm.select().where(LaborStatusForm.POSN_CODE << deptPositions))

    cfbd = list(model_to_dict(c) for c in currentFormsByDept)
    pfbd = list(model_to_dict(p) for p in pastFormsByDept)

    allDepartmentStudents = cfbd + [""] + pfbd  # NOTE: The empty value is to separate current and past when processing in the JS

    return json.dumps(allDepartmentStudents)

    # except Exception as e:
    #     print('ERROR in Department Students:', e)
    #     return jsonify({"Success": False})
