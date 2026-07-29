from datetime import date

from flask import g, request, redirect, jsonify

from app.controllers.admin_routes import *
from app.login_manager import require_login

from app.controllers.admin_routes import admin
from app.controllers.errors_routes.handlers import *

from app.models.formHistory import FormHistory
from app.models.user import *
from app.models.term import *
from app.models.department import *
from app.models.allocation import *
from app.models.laborStatusForm import *

from app.logic.manageDepartments import * 



# FIXME: The default value year should be the current academic year (Rather than waiting to be clicked it should be on the current year by default).
@admin.route('/admin/manageDepartments/', methods=['GET'])
@admin.route('/admin/manageDepartments/<academicYear>', methods=['GET']) 
def manageDepartments(academicYear = None):
    """
    Updates the Labor Status Forms database with any new departments in the Tracy database on page load.
    Returns the departments to be used in the HTML for the manage departments page.
    """

    currentUser = require_login()
    if not currentUser:                    # If the current user is not logged in
        return render_template('errors/403.html')
    if not currentUser.isLaborAdmin:       # If the currrent user is not an admin
        if currentUser.student: # If the currrent user is logged in as a student
            return redirect('/laborHistory/' + currentUser.student.ID)
        elif currentUser.supervisor:
            return render_template('errors/403.html'), 403


    # The condition below may be deleted if the routing to the Manage Departments page is changed. 
    if academicYear == None: 
        academicYear = g.openTerm.termCode
    else: 
        academicYear = int(academicYear)


    currentAY, previousAY, nextAY = generateAdjacentYears(academicYear)
    chosenAY = Term.get(Term.termCode == academicYear)


    # FIXME: REPLACE str(row["totalHours"] if row["totalHours"] is not None else 0) WITH SOMETHING BETTER, LIKE str(row["totalHours"] or 0)
    breakHoursByDepartment = {row["department"]: str(row["totalHours"] or 0) for row in getUsedBreakHours(chosenAY)} 
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
                            currentAY = currentAY,
                            previousAY = previousAY,
                            nextAY = nextAY,
                            academicYear = chosenAY.termName,
                            breakHoursByDepartment = breakHoursByDepartment,
                            allocationStatus = allocationStatus
                            )



@admin.route('/admin/complianceStatus', methods=['POST'])
def complianceStatusCheck():
    """
    This function changes the compliance status in the database for labor status forms.  It works in collaboration with the ajax call in manageDepartments.js
    """
    try:
        rsp = request.get_json()
        if rsp:
            department = Department.get(int(rsp['deptName']))
            department.departmentCompliance = not department.departmentCompliance
            department.save()
            return jsonify({"Success": True})
    except Exception as e:
        print(e)
        return jsonify({"Success": False})
