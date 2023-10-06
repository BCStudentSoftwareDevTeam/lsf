from app.controllers.admin_routes import *
from app.models.user import *
from app.models.supervisorDepartment import SupervisorDepartment
from app.login_manager import require_login
from app.logic.search import getSupervisorsForDepartment
from app.controllers.admin_routes import admin
from app.controllers.errors_routes.handlers import *
#from app.models.manageDepartments import *
from app.models.term import *
from flask_bootstrap import bootstrap_find_resource
from app.models.department import *
from flask import request, redirect
from flask import jsonify
from playhouse.shortcuts import model_to_dict
from app.logic.tracy import Tracy

@admin.route('/admin/manageDepartments', methods=['GET'])
# @login_required
def manage_departments():
    """
    Updates the Labor Status Forms database with any new departments in the Tracy database on page load.
    Returns the departments to be used in the HTML for the manage departments page.
    """
    try:
        currentUser = require_login()
        if not currentUser:                    # Not logged in
            return render_template('errors/403.html')
        if not currentUser.isLaborAdmin:       # Not an admin
            if currentUser.student: # logged in as a student
                return redirect('/laborHistory/' + currentUser.student.ID)
            elif currentUser.supervisor:
                return render_template('errors/403.html'), 403

        departmentTracy = Tracy().getDepartments()
        allSupervisors= Supervisor.select().order_by(Supervisor.LAST_NAME)
        for dept in departmentTracy:
            d, created = Department.get_or_create(DEPT_NAME = dept.DEPT_NAME, ACCOUNT=dept.ACCOUNT, ORG = dept.ORG)
            d.save()
        department = Department.select()
        return render_template( 'admin/manageDepartments.html',
                                title = ("Manage Departments"),
                                department = department,
                                allSupervisors = allSupervisors
                                )
    except Exception as e:
        print("Error Loading all Departments", e)
        return render_template('errors/500.html'), 500

@admin.route("/admin/manageDepartments/<departmentID>", methods=['GET'])
def getSupervisorsinDepartment(departmentID):
    try:
        currentUser = require_login()
        if not currentUser:                    # Not logged in
            return render_template('errors/403.html')
        if not currentUser.isLaborAdmin:       # Not an admin
            if currentUser.student: # logged in as a student
                return redirect('/laborHistory/' + currentUser.student.ID)
            elif currentUser.supervisor:
                return render_template('errors/403.html'), 403
        
        supervisors = getSupervisorsForDepartment(departmentID)
        departmentID=Department.get_by_id(departmentID)
        supervisors= [model_to_dict(supervisor) for supervisor in supervisors]
        return jsonify([model_to_dict(departmentID), supervisors])
    except Exception as e:
        return render_template('errors/500.html'), 500
    
@admin.route('/admin/manageDepartments/removeSupervisorFromDepartment', methods=['POST'])
def removeSupervisorFromDepartment():
    try:
        currentUser = require_login()
        if not currentUser:                    # Not logged in
            return render_template('errors/403.html')
        if not currentUser.isLaborAdmin:       # Not an admin
            if currentUser.student: # logged in as a student
                return redirect('/laborHistory/' + currentUser.student.ID)
            elif currentUser.supervisor:
                return render_template('errors/403.html'), 403
        
        formData = request.form
        supervisorDeptRecord = SupervisorDepartment.get_or_none(supervisor = formData['supervisorID'], department = formData['departmentID'])
    
        if supervisorDeptRecord:
            supervisorDeptRecord.delete_instance()
            return "True"
        else:
            return "False"
    
    except Exception as e:
        print(f'Could not remove user from department: {e}')
        return "", 500

@admin.route('/admin/complianceStatus', methods=['POST'])
def complianceStatusCheck():
    """
    This function changes the compliance status in the database for labor status forms.  It works in collaboration with the ajax call in manageDepartments.js
    """
    try:
        rsp = eval(request.data.decode("utf-8")) # This fixes byte indices must be intergers or slices error
        if rsp:
            department = Department.get(int(rsp['deptName']))
            department.departmentCompliance = not department.departmentCompliance
            department.save()
            return jsonify({"Success": True})
    except Exception as e:
        print(e)
        return jsonify({"Success": False})
