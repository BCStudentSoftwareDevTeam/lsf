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
from flask_bootstrap import bootstrap_find_resource
from app.models.department import *
from app.models.allocation import *
from app.models.laborStatusForm import * #Do we need to import all?
from flask import request, redirect
from flask import jsonify
from playhouse.shortcuts import model_to_dict
from app.logic.tracy import Tracy
from datetime import date
from flask import g
from app.logic.manageDepartments import * # Reorganize imports to avoid circular import issues.  This is a temporary fix, but it works for now.

@admin.route('/admin/manageDepartments/', methods=['GET'])
@admin.route('/admin/manageDepartments/<academic_year>', methods=['GET'])
# @login_required
def manage_departments(academic_year = None):     # FIXME
    """
    Updates the Labor Status Forms database with any new departments in the Tracy database on page load.
    Returns the departments to be used in the HTML for the manage departments page.
    """
    print ("######################", g.openTerm.termName, "######################")
    try:
        currentUser = require_login()
        if not currentUser:                    # Not logged in
            return render_template('errors/403.html')
        if not currentUser.isLaborAdmin:       # Not an admin
            if currentUser.student: # logged in as a student
                return redirect('/laborHistory/' + currentUser.student.ID)
            elif currentUser.supervisor:
                return render_template('errors/403.html'), 403
        
        # Sets academic_year to the current open term if no academic year is provided in the URL. Current solution. WILL change in the future.
        if not academic_year:
            academic_year = g.openTerm.termCode
        
        fall_suffix = 11 # Ex.) Fall 2025 = 202511
        spring_suffix = 12 # Ex.) Spring 2026 = 202512 
        summer_suffix = 13 # Ex.) Summer 2026 = 202513

        currentTerm = Term.get(Term.termCode == academic_year)
        previousTerm = Term.get(Term.termCode == academic_year - 100)
        nextTerm = Term.get(Term.termCode == academic_year + 100)



        # Works. Just use production data to test. Add demo data for this later. (This was a request from Labor Office to have the ability to view based on term.)
        # fallTerm = Term.get(Term.termCode == academic_year + fall_suffix)
        # springTerm = Term.get(Term.termCode == academic_year + spring_suffix)
        # summerTerm = Term.get(Term.termCode == academic_year + summer_suffix)

        # print("******************",fallTerm.termName, springTerm.termName, summerTerm.termName, "**********************")
        # print("******************",previousTerm.termName, nextTerm.termName, currentTerm.termName, "**********************")

        # totalBreakSum = getUsedBreakHours(currentTerm)

        # print("Something\n\n")

        
        # for row in totalBreakSum:
        #     print(row['department'],int(row['totalHours']),row['termCode'])
        #     print(totalBreakSum)

        breakHoursByDepartment = {row["department"]: str(row["totalHours"] if row["totalHours"] is not None else 0) for row in getUsedBreakHours(currentTerm)} # I think Scott wanted this to say NULL not zero, unsure.

        # print(breakHoursByDepartment)

        # print("\n\nSomething")

        # activeDepartments = Department.select().where(Department.isActive == True)
        # allAllocations = Allocation.select().where(Allocation.termCode == currentTerm)
        inactiveDepartments = Department.select().where(Department.isActive == False)
        
        
        activeDepartments = getActiveDepartmentsWithAllocation(currentTerm)
        
        # Move some of this to Logic (maybe).
        for dept in activeDepartments:
            dept.totalPrimaries = (dept.allocation.primary_10 + dept.allocation.primary_12 + dept.allocation.primary_15 + dept.allocation.primary_20)
            dept.totalSecondaries = (dept.allocation.secondary_5 + dept.allocation.secondary_10)

            lsfCountPrimaries = getLSFCountPrimaries(currentTerm, dept)
            lsfCountSecondaries = getLSFCountSecondaries(currentTerm, dept)
            dept.lsfCountPrimaries = lsfCountPrimaries
            dept.lsfCountSecondaries = lsfCountSecondaries
        # print("######################")
        # print(f"COUNTS: {lsfCountSecondaries} ")
        # print([lsf.formID for lsf in lsfCountPrimaries])
        # print([lsf.formID for lsf in lsfCountSecondaries])

        allocationStatus = {
            department.departmentID: getAllocationStatus(currentTerm, department)
            for department in activeDepartments
        }

        # print("Pizza\n\n\n\n")
        # print ("Allocation Status:", allocationStatus)
        # print("\n\n\n\nPotato")

        

        allSupervisors= Supervisor.select().order_by(Supervisor.LAST_NAME)
        return render_template( 'admin/manageDepartments.html',
                                title = ("Manage Departments"),
                                activeDepartments = activeDepartments,
                                inactiveDepartments = inactiveDepartments,
                                allSupervisors = allSupervisors,
                                currentTerm = currentTerm.termName,
                                previousTerm = previousTerm.termName,
                                nextTerm = nextTerm.termName,
                                academicYear = currentTerm.termName,
                                # totalBreakSum = totalBreakSum
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
        rsp = eval(request.data.decode("utf-8")) # This fixes byte indices must be intergers or slices error
        if rsp:
            department = Department.get(int(rsp['deptName']))
            department.departmentCompliance = not department.departmentCompliance
            department.save()
            return jsonify({"Success": True})
    except Exception as e:
        print(e)
        return jsonify({"Success": False})
