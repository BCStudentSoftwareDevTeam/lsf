from datetime import date

from flask import g, request, redirect, jsonify
from flask_bootstrap import bootstrap_find_resource
from playhouse.shortcuts import model_to_dict

from app.controllers.admin_routes import *
from app.models import term
from app.models.formHistory import FormHistory
from app.models.user import *
from app.models.supervisorDepartment import SupervisorDepartment
from app.login_manager import require_login
from app.logic.search import getSupervisorsForDepartment
from app.controllers.admin_routes import admin
from app.controllers.errors_routes.handlers import *
from app.models.term import *
from app.models.department import *
from app.models.allocation import *
from app.models.laborStatusForm import *
from app.logic.tracy import Tracy
from app.logic.manageDepartments import * # Reorganize imports to avoid circular import issues.  This is a temporary fix, but it works for now.
from app.controllers.admin_routes.termManagement import createTerms



@admin.route('/admin/manageDepartments/', methods=['GET'])
@admin.route('/admin/manageDepartments/<academicYear>', methods=['GET']) 
# FIXME: The default value year should be the current academic year (Rather than waiting to be clicked it should be on the current year by default).

# @login_required
def manage_departments(academicYear = None):
    """
    Updates the Labor Status Forms database with any new departments in the Tracy database on page load.
    Returns the departments to be used in the HTML for the manage departments page.
    """

    try:

        checkAdmistratorRights()

        if academicYear == None: 
            academicYear = g.openTerm.termCode
        else: 
            academicYear = int(academicYear)

        previousAYTerms, currentAYTerms, nextAYTerms = generateTermsForAdjacentYears(academicYear)
        chosenAY = Term.get(Term.termCode == academicYear)


        breakHoursByDepartment = {row["department"]: str(row["totalHours"] if row["totalHours"] is not None else 0) for row in getUsedBreakHours(chosenAY)} 
        # I think Scott wanted this to say NULL not zero, unsure.


        activeDepartments = getActiveDepartmentsWithAllocation(chosenAY)
        inactiveDepartments = Department.select().where(Department.isActive == False)  
        

        allocationStatus = {
            department.departmentID: getAllocationStatus(chosenAY, department)
            for department in activeDepartments
        }

        allSupervisors= Supervisor.select().order_by(Supervisor.LAST_NAME)

        return render_template( 'admin/manageDepartments.html',
                                activeDepartments = activeDepartments,
                                inactiveDepartments = inactiveDepartments,
                                allSupervisors = allSupervisors,
                                currentAY = currentAYTerms[0],
                                previousAY = previousAYTerms[0],
                                nextAY = nextAYTerms[0],
                                academicYear = chosenAY.termName,
                                breakHoursByDepartment = breakHoursByDepartment,
                                allocationStatus = allocationStatus
                                )
    except Exception as e:
        print("Error Loading all Departments", e)
        return render_template('errors/500.html'), 500



@admin.route("/admin/manageDepartments/<departmentID>", methods=['GET'])
def getSupervisorsInDepartment(departmentID):
        currentUser = require_login()
        if not currentUser:                    # Not logged in
            return render_template('errors/403.html')
        if not currentUser.isLaborAdmin:       # Not an admin
            if currentUser.student: # logged in as a student
                return redirect('/laborHistory/' + currentUser.student.ID)
            elif currentUser.supervisor:
                return render_template('errors/403.html'), 403
        
        supervisors = getSupervisorsForDepartment(departmentID)
        supervisors = [model_to_dict(supervisor) for supervisor in supervisors]
        return jsonify(supervisors)
    


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
        rsp = request.get_json() # This fixes byte indices must be intergers or slices error
        if rsp:
            department = Department.get(int(rsp['deptName']))
            department.departmentCompliance = not department.departmentCompliance
            department.save()
            return jsonify({"Success": True})
    except Exception as e:
        print(e)
        return jsonify({"Success": False})
