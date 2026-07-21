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
from app.controllers.admin_routes.termManagement import createTerms
@admin.route('/admin/manageDepartments/', methods=['GET'])
@admin.route('/admin/manageDepartments/<academic_year>', methods=['GET']) # FIXME: The default value year should be the current academic year (Rather than waiting to be clicked it should be on the current year by default).
# @login_required
def manage_departments(academic_year = None):
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
        else:
            academic_year = int(academic_year)

        currentAY = Term.get(Term.termCode == academic_year)
        print("Current Term:", currentAY.termName)

        previousAcademicYear = (academic_year - 100) // 100
        createPreviousAY = createTerms(previousAcademicYear)
        previousAY = createPreviousAY[0]
        print("Previous Term:", previousAY.termName)

        nextAcademicYear = (academic_year + 100) // 100
        createNextAY = createTerms(nextAcademicYear)
        nextAY = createNextAY[0]
        print("Next Term:", nextAY.termName)
        
        # Works. Should work without production data now.
        # We've also thought about having a drop down menu to select the term once the academic year is selected. This should also include the ability to view the entire academic year.
        # Given the new implementation of the term management page, we can now use the term management page to create terms for the academic year and then use this page to view the departments for that academic year.  This will be a much more efficient way to manage the terms and departments.
        # A concept of Currently Selected Term does not exist, yet. Implementing it here will make it so that the user can select a term and then view the departments for that term.  This will be a much more efficient way to manage the terms and departments.
        plainAcademicYear = academic_year // 100 # Might be a good idea to create a function for // 100 since it appears in multiple places.  This will make it easier to change the implementation in the future if needed.
        createdTerms = createTerms(plainAcademicYear) #FIXME: Use the selected academic year to create the terms for that year.  This will be a much more efficient way to manage the terms and departments.
        fallTerm = createdTerms[1]
        springTerm = createdTerms[4]
        summerTerm = createdTerms[6]

        print("******************",fallTerm.termName, springTerm.termName, summerTerm.termName, "**********************")
        print("******************",previousAY.termName, nextAY.termName, currentAY.termName, "**********************")

        # For Testing Purposes.  This will be removed once the term management page is fully implemented and the terms are created for the academic year.
        # totalBreakSum = getUsedBreakHours(currentAY)
        # for row in totalBreakSum:
        #     print(row['department'],int(row['totalHours']),row['termCode'])
        #     print(totalBreakSum)

        breakHoursByDepartment = {row["department"]: str(row["totalHours"] if row["totalHours"] is not None else 0) for row in getUsedBreakHours(currentAY)} # I think Scott wanted this to say NULL not zero, unsure.

        # print(breakHoursByDepartment)

        # print("\n\nSomething")

        # This was left just incase anything went wrong. Delete this if everything works as expected. Not nessicary in current implementation.
        # activeDepartments = Department.select().where(Department.isActive == True)
        # allAllocations = Allocation.select().where(Allocation.termCode == currentAY)

        inactiveDepartments = Department.select().where(Department.isActive == False)
        
        
        activeDepartments = getActiveDepartmentsWithAllocation(currentAY)
        
        # Move some of this to Logic.
        for dept in activeDepartments:
            dept.totalPrimaries = (dept.allocation.primary_10 + dept.allocation.primary_12 + dept.allocation.primary_15 + dept.allocation.primary_20)
            dept.totalSecondaries = (dept.allocation.secondary_5 + dept.allocation.secondary_10)

            lsfCountPrimaries = getLSFCountPrimaries(currentAY, dept)
            lsfCountSecondaries = getLSFCountSecondaries(currentAY, dept)
            dept.lsfCountPrimaries = lsfCountPrimaries
            dept.lsfCountSecondaries = lsfCountSecondaries
        # print("######################")
        # print(f"COUNTS: {lsfCountSecondaries} ")
        # print([lsf.formID for lsf in lsfCountPrimaries])
        # print([lsf.formID for lsf in lsfCountSecondaries])

        allocationStatus = {
            department.departmentID: getAllocationStatus(currentAY, department)
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
                                currentAY = currentAY.termName,
                                previousAY = previousAY.termName,
                                nextAY = nextAY.termName,
                                academicYear = currentAY.termName,
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
