from datetime import date

from flask import g, request, redirect, jsonify, abort

from app.controllers.admin_routes import *
from app.login_manager import require_login

from app.controllers.admin_routes import admin
from app.controllers.errors_routes.handlers import *
from app.logic.getPositions import getToBeReviewedPosition
from app.models.formHistory import FormHistory
from app.models.user import *
from app.models.term import *
from app.models.department import *
from app.models.allocation import *
from app.models.laborStatusForm import *

from app.logic.manageDepartments import * 



@admin.route('/admin/manageDepartments/', methods=['GET'])
@admin.route('/admin/manageDepartments/<academicYear>', methods=['GET']) 
def manageDepartments(academicYear = None):
    """
    Returns the Manage Departments page, which allows the admin to view all the departments
    and their allocations.  
    """

    # Checking Admin Rights
    currentUser = require_login()
    if not currentUser:                    # If the current user is not logged in
        return render_template('errors/403.html')
    if not currentUser.isLaborAdmin:   
        if currentUser.student:
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

    breakHoursByDepartment = {row["department"]: str(row["totalHours"] or 0) for row in getUsedBreakHours(chosenAY)}

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
    This function changes the compliance status in the database for labor status forms.  
    It works in collaboration with the ajax call in manageDepartments.js
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



@admin.route('/admin/manageDepartments/<org>/<account>/allocationReview', methods=['GET'])
def allocationReview(org=None, account=None):
    """
    Returns the Allocation Review page/form, which can only be accessed through
    the Manage Departments page.  
    """

    # Retrieving the departments based on the org and account numbers 
    try:
        dept = Department.get(Department.ORG == org, Department.ACCOUNT == account)
    except (NameError, DoesNotExist):
        abort(404)
    
    # Checking admin rights
    currentUser = require_login()
    if not currentUser:                    # If the current user is not logged in
        return render_template('errors/403.html')
    if not currentUser.isLaborAdmin: 
        if currentUser.student:
            return redirect('/laborHistory/' + currentUser.student.ID)
        elif currentUser.supervisor:
            return render_template('errors/403.html'), 403

    # Retrieving the next year 
    # DON'T DELETE THE UNDERSCORES
    _, _, nextAY = generateAdjacentYears()
    # The generateAdjacentYears() function returns a tuple of three elements, and we only need the third value

    return render_template('admin/allocationReview.html', department = dept, nextAY = nextAY)


@admin.route('/admin/manageDepartments/<org>/<account>/positionreview', methods=['GET'])
def positionreview(org=None, account=None):
    try:
        dept = Department.get(Department.ORG == org, Department.ACCOUNT == account)
    except (NameError, DoesNotExist):
        abort(404)

    positionsList = getToBeReviewedPosition(dept) 

    return render_template('admin/positionreview.html',
                            positions = positionsList
    )