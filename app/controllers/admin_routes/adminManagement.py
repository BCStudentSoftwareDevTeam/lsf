from app.controllers.admin_routes import *
from app.models.user import *
from app.controllers.admin_routes import admin
from flask import request
from app.login_manager import require_login
from flask import Flask, redirect, url_for, flash, jsonify
from app.models.supervisor import Supervisor
from app.models.student import Student
from app.logic.tracy import Tracy
from app.logic.userInsertFunctions import createStudentFromTracy, createSupervisorFromTracy, createUser
from app.logic.adminManagement import searchForAdmin, getUser
from app.logic.utils import adminFlashMessage


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

    users = (User.select(User,Supervisor,Student)
                .join(Supervisor,join_type=JOIN.LEFT_OUTER).switch()
                .join(Student,join_type=JOIN.LEFT_OUTER))
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
        userList = searchForAdmin(rsp)
        return jsonify(userList)
    except Exception as e:
        print('ERROR Loading Non Labor Admins:', e, type(e))
        return jsonify(userList)

@admin.route("/adminManagement/userInsert", methods=['POST'])
def manageLaborAdmin():
    actionMap = {
    "addLaborAdmin":     {"selectPickerID": "addAdmin",                "type": "Labor",        "action": "add",    "pretty": "Labor"},
    "removeLaborAdmin":  {"selectPickerID": "removeAdmin",             "type": "Labor",        "action": "remove", "pretty": "Labor"},
    "addFinAidAdmin":    {"selectPickerID": "addFinancialAidAdmin",    "type": "FinancialAid", "action": "add",    "pretty": "Financial Aid"},
    "removeFinAidAdmin": {"selectPickerID": "removeFinancialAidAdmin", "type": "FinancialAid", "action": "remove", "pretty": "Financial Aid"},
    "addSaasAdmin":      {"selectPickerID": "addSAASAdmin",            "type": "Saas",         "action": "add",    "pretty": "SAAS"},
    "removeSaasAdmin":   {"selectPickerID": "removeSAASAdmin",         "type": "Saas",         "action": "remove", "pretty": "SAAS"},
    }    

    key = request.form.get('action')
    meta = actionMap[key]
    user = getUser(actionMap[key]['selectPickerID'])

    # pick addAdmin or removeAdmin dynamically
    if meta['action'] == 'add':
        addAdmin(user, meta['type'])
    else:
        removeAdmin(user, meta['type'])
    
    flashMessage(user, 
                    'added' if meta["action"] == "add" else 'removed', 
                    meta["pretty"])
             
    return redirect(url_for('admin.admin_Management'))

def addAdmin(user, adminType):
    setattr(user, f"is{adminType}Admin", True)
    user.save()

def removeAdmin(user, adminType):
    setattr(user, f"is{adminType}Admin", False)
    user.save()

def flashMessage(user, action, adminType):
    message = "{} has been {} as a {} Admin".format(user.fullName, action, adminType)
    flash(message, "success")
