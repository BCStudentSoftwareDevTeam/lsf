from app.controllers.admin_routes import *
from app.models.user import User, DoesNotExist
from app.models.user import *
from app.controllers.admin_routes import admin
from flask import request
from app.login_manager import require_login
from flask import Flask, redirect, url_for, flash, jsonify
from app.models.supervisor import Supervisor
from app.models.student import Student
from app.logic.tracy import Tracy
from app.logic.userInsertFunctions import createUser, createSupervisorFromTracy, createStudentFromTracy

@admin.route('/admin/adminManagement', methods=['GET'])
# @login_required
def admin_Management():
# username = load_user('heggens')
    currentUser = require_login()
    if not currentUser:                    # Not logged in
        return render_template('errors/403.html'), 403
    if not currentUser.isLaborAdmin:       # Not an admin
        if currentUser.student: # logged in as a student
            return redirect('/laborHistory/' + currentUser.student.ID)
        elif currentUser.supervisor:
            return render_template('errors/403.html'), 403

    users = User.select()
    return render_template( 'admin/adminManagement.html',
                            title=('Admin Management'),
                            users = users
                         )

@admin.route('/admin/adminSearch', methods=['POST'])
def adminSearch():
    """
    This function takes in the data from the 'Add Labor Admin' select picker, then uses the data to query from the User table and return a list of possible options
    to populate the select picker.
    """
    try:
        rsp = eval(request.data.decode("utf-8"))
        userInput = rsp[1]
        adminType = rsp[0]
        userList = []
        if adminType == "addlaborAdmin":
            tracyStudents = Tracy().getStudentsFromUserInput(userInput)
            students = []
            for student in tracyStudents:
                try:
                    existingUser = User.get(User.student == student.ID)
                    if existingUser.isLaborAdmin:
                        pass
                    else:
                        students.append(student)
                except DoesNotExist as e:
                    students.append(student)
            for student in students:
                username = student.STU_EMAIL.split('@', 1)
                userList.append({'username': username[0],
                                'firstName': student.FIRST_NAME,
                                'lastName': student.LAST_NAME,
                                'type': 'Student'
                                })
        tracySupervisors = Tracy().getSupervisorsFromUserInput(userInput)
        supervisors = []
        for supervisor in tracySupervisors:
            try:
                existingUser = User.get(User.supervisor == supervisor.ID)
                if ((existingUser.isLaborAdmin and adminType == "addlaborAdmin")
                    or (existingUser.isSaasAdmin and adminType == "addSaasAdmin")
                    or (existingUser.isFinancialAidAdmin and adminType == "addFinAidAdmin")):
                    pass
                else:
                    supervisors.append(supervisor)
            except DoesNotExist as e:
                supervisors.append(supervisor)
        for sup in supervisors:
            username = sup.EMAIL.split('@', 1)
            userList.append({'username': username[0],
                            'firstName': sup.FIRST_NAME,
                            'lastName': sup.LAST_NAME,
                            'type': 'Supervisor'})
        return jsonify(userList)
    except Exception as e:
        print('ERROR Loading Non Labor Admins:', e, type(e))
        return jsonify(userList)

@admin.route("/adminManagement/userInsert", methods=['POST'])
def manageLaborAdmin():
    if request.form.get("addAdmin"):
        newAdmin = getUser('addAdmin')
        addAdmin(newAdmin, 'labor')
        flashMessage(newAdmin, 'added', 'Labor')

    elif request.form.get("removeAdmin"):
        oldAdmin = getUser('removeAdmin')
        removeAdmin(oldAdmin, 'labor')
        flashMessage(oldAdmin, 'removed', 'Labor')

    elif request.form.get("addFinancialAidAdmin"):
        newAdmin = getUser('addFinancialAidAdmin')
        addAdmin(newAdmin, 'finAid')
        flashMessage(newAdmin, 'added', 'Financial Aid')

    elif request.form.get("removeFinancialAidAdmin"):
        oldAdmin = getUser('removeFinancialAidAdmin')
        removeAdmin(oldAdmin, 'finAid')
        flashMessage(oldAdmin, 'removed', 'Financial Aid')

    elif request.form.get("addSAASAdmin"):
        newAdmin = getUser('addSAASAdmin')
        addAdmin(newAdmin, 'saas')
        flashMessage(newAdmin, 'added', 'SAAS')

    elif request.form.get("removeSAASAdmin"):
        oldAdmin = getUser('removeSAASAdmin')
        removeAdmin(oldAdmin, 'saas')
        flashMessage(oldAdmin, 'removed', 'SAAS')

    return redirect(url_for('admin.admin_Management'))

def getUser(selectpickerID):
    username = request.form.get(selectpickerID)
    try:
        user = User.get(User.username == username)
    except DoesNotExist as e:
        usertype = Tracy().checkStudentOrSupervisor(username)
        supervisor = student = None
        if usertype == "Student":
            student = createStudentFromTracy(username)
        else:
            supervisor = createSupervisorFromTracy(username)
        user = createUser(username, student=student, supervisor=supervisor)
    return user

def addAdmin(newAdmin, adminType):
    if adminType == 'labor':
        newAdmin.isLaborAdmin = True
    if adminType == 'finAid':
        newAdmin.isFinancialAidAdmin = True
    if adminType == 'saas':
        newAdmin.isSaasAdmin = True
    newAdmin.save()

def removeAdmin(oldAdmin, adminType):
    if adminType == 'labor':
        oldAdmin.isLaborAdmin = False
    if adminType == 'finAid':
        oldAdmin.isFinancialAidAdmin = False
    if adminType == 'saas':
        oldAdmin.isSaasAdmin = False
    oldAdmin.save()

def flashMessage(user, action, adminType):
    message = "{} has been {} as a {} Admin".format(user.fullName, action, adminType)

    if action == 'added':
        flash(message, "success")
    elif action == 'removed':
        flash(message, "danger")
