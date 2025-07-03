from app.controllers.admin_routes import *
from app.models.user import *
from app.controllers.admin_routes import admin
from flask import request
from app.login_manager import require_login
from flask import Flask, redirect, url_for, flash, jsonify
from app.models.supervisor import Supervisor
from app.models.student import Student
from app.logic.tracy import Tracy, createStudentFromTracy
from app.logic.userInsertFunctions import createSupervisorFromTracy, createUser
from app.logic.adminManagement import searchForAdmin,  getUser, addAdmin, removeAdmin
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
        userList = searchForAdmin(rsp)
        return jsonify(userList)
    except Exception as e:
        print('ERROR Loading Non Labor Admins:', e, type(e))
        return jsonify(userList)

@admin.route("/adminManagement/userInsert", methods=['POST'])
def manageLaborAdmin():
    if request.form.get("addAdmin"):
        newAdmin = getUser('addAdmin')
        addAdmin(newAdmin, 'labor')
        adminFlashMessage(newAdmin, 'added', 'Labor')

    elif request.form.get("removeAdmin"):
        oldAdmin = getUser('removeAdmin')
        removeAdmin(oldAdmin, 'labor')
        adminFlashMessage(oldAdmin, 'removed', 'Labor')

    elif request.form.get("addFinancialAidAdmin"):
        newAdmin = getUser('addFinancialAidAdmin')
        addAdmin(newAdmin, 'finAid')
        adminFlashMessage(newAdmin, 'added', 'Financial Aid')

    elif request.form.get("removeFinancialAidAdmin"):
        oldAdmin = getUser('removeFinancialAidAdmin')
        removeAdmin(oldAdmin, 'finAid')
        adminFlashMessage(oldAdmin, 'removed', 'Financial Aid')

    elif request.form.get("addSAASAdmin"):
        newAdmin = getUser('addSAASAdmin')
        addAdmin(newAdmin, 'saas')
        adminFlashMessage(newAdmin, 'added', 'SAAS')

    elif request.form.get("removeSAASAdmin"):
        oldAdmin = getUser('removeSAASAdmin')
        removeAdmin(oldAdmin, 'saas')
        adminFlashMessage(oldAdmin, 'removed', 'SAAS')

    return redirect(url_for('admin.admin_Management'))

