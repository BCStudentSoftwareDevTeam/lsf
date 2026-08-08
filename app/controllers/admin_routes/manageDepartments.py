from datetime import date

from flask import g, request, redirect, jsonify, abort

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

from playhouse.shortcuts import model_to_dict

@admin.route('/admin/manageDepartments/', methods=['GET'])
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

    currentAY, nextAY = generateAdjacentYears(g.openTerm.termCode)
    
    inactiveDepartments = Department.select().where(Department.isActive == False)  
    allSupervisors = Supervisor.select().order_by(Supervisor.LAST_NAME)

    breakHoursByDepartment = {row["department"]: str(row["totalHours"] or 0) for row in getUsedBreakHours(currentAY)}

    activeDepartmentsAllocations = getActiveDepartmentsAllocations(currentAY,nextAY)                       

    return render_template( 'admin/manageDepartments.html',
                            activeDepartmentsAllocations = activeDepartmentsAllocations,
                            inactiveDepartments = inactiveDepartments,
                            allSupervisors = allSupervisors,                 
                            currentAY = currentAY,
                            nextAY = nextAY,
                            breakHoursByDepartment = breakHoursByDepartment,
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