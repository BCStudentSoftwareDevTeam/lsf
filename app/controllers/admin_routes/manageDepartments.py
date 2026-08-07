from datetime import date

from flask import g, request, redirect, jsonify, abort, flash

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
from app.logic.allocationManager import allocationExists
from app.logic.academicYearManager import getCurrentAndNextAY



@admin.route('/admin/manageDepartments/', methods=['GET'])
def manageDepartments():
    """
    Returns the Manage Departments page, which allows the admin to view all the departments
    and their allocations.  
    """

    # Checking Admin Rights
    currentUser = require_login()
    if not currentUser:                    # If the current user is not logged in
        return render_template('errors/403.html')
    if not (currentUser.isLaborAdmin or currentUser.isLaborDepartmentStudent):   
        if currentUser.student:
            return redirect('/laborHistory/' + currentUser.student.ID)
        elif currentUser.supervisor:
            return render_template('errors/403.html'), 403

    currentAY, nextAY = getCurrentAndNextAY()
    chosenAY = Term.get(Term.termCode == currentAY.termCode)

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


    # getting the name of the currently chosen department (based on the org and account numbers)
    try:
        dept = Department.get(Department.ORG == org, Department.ACCOUNT == account)
    except (NameError, DoesNotExist):
        abort(404)
    

    # Checking admin rights
    currentUser = require_login()
    if not currentUser:                    # If the current user is not logged in
        return render_template('errors/403.html')
    if not (currentUser.isLaborAdmin or currentUser.isLaborDepartmentStudent): 
        if currentUser.student:
            return redirect('/laborHistory/' + currentUser.student.ID)
        elif currentUser.supervisor:
            return render_template('errors/403.html'), 403


    # Retrieving the current and following academic years
    currentAY, nextAY = getCurrentAndNextAY()


    # checking if the allocation has already been approved
    if allocationExists(nextAY.termCode, dept, isFinal=True): 
        flash("You cannot reapprove an allocation request.", "danger")
        return redirect('/admin/manageDepartments/')

    
    # checking if the department has requested any allocation review 
    if not allocationExists(nextAY.termCode, dept, isFinal=False):
        flash(f"The {dept.DEPT_NAME} department has not requested an allocation review yet.", "danger")
        return redirect('/admin/manageDepartments/')


    # getting the current and the requested allocations
    currentAlloc = Allocation.get_or_none(Allocation.termCode == currentAY.termCode, Allocation.department == dept, Allocation.isFinal == True)
    requestedAlloc = Allocation.get(Allocation.termCode == nextAY.termCode, Allocation.department == dept, Allocation.isFinal == False)


    return render_template('admin/allocationReview.html',
                            department = dept, 
                            nextAY = nextAY,
                            currentAlloc = currentAlloc,
                            requestedAlloc = requestedAlloc
                            )



@admin.route('/admin/allocationReview/approve', methods=['POST'])
def approveAllocationReview():
    
    # Retrieving the current and following academic years
    currentAY, nextAY = getCurrentAndNextAY()

    # getting the ID of the user who approves the request
    approverID = require_login().userID

    # getting the name of the requesting department
    requester = request.form.get("requester", type=int, default=None)

    # saving the newly approved allocation
    newApprovedAlloc = Allocation.create(termCode       = nextAY.termCode, 
                                        department      = requester, 
                                        isFinal         = True,
                                        approvedBy      = approverID,
                                        approvedOn      = date.today(),
                                        primary_10      = request.form.get("primary_10", type=int, default=None),
                                        primary_12      = request.form.get("primary_12", type=int, default=None),
                                        primary_15      = request.form.get("primary_15", type=int, default=None),
                                        primary_20      = request.form.get("primary_20", type=int, default=None),
                                        secondary_5     = request.form.get("secondary_5", type=int, default=None),
                                        secondary_10    = request.form.get("secondary_10", type=int, default=None),
                                        breakHours      = request.form.get("breakHours", type=int, default=None)
                                        )
    newApprovedAlloc.save()

    return redirect("/admin/manageDepartments")
