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
    currentAY, _, nextAY = generateAdjacentYears()
    

    # getting the current allocation
    currentAlloc = Allocation.get(Allocation.termCode == currentAY.termCode, Allocation.department == dept, Allocation.isFinal == True)


    # checking if the department has requested any allocation review 
    requestedAlloc = Allocation.get_or_none(Allocation.termCode == nextAY.termCode, Allocation.department == dept, Allocation.isFinal == False)
    isRequested    = bool(requestedAlloc)
    if not isRequested: 
        flash(f"The {dept.DEPT_NAME} department has not requested an allocation review yet.", "danger")
        return redirect('/admin/manageDepartments/')


    # checking if the allocation has already been approved
    isApproved = bool(Allocation.get_or_none(Allocation.termCode == nextAY.termCode, Allocation.department == dept, Allocation.isFinal == True))
    if isApproved: 
        flash("You cannot reapprove an allocation request.", "danger")
        return redirect('/admin/manageDepartments/')


    return render_template('admin/allocationReview.html',
                            department = dept, 
                            nextAY = nextAY,
                            requestedAlloc = requestedAlloc,
                            currentAlloc = currentAlloc
                            )



@admin.route('/admin/allocationReview/approve', methods=['POST'])
def approveAllocationReview():
    
    # Retrieving the next year 
    # DON'T DELETE THE UNDERSCORES
    currentAY, _, nextAY = generateAdjacentYears()


    currentAlloc = Allocation.get(
                                Allocation.termCode     == currentAY.termCode, 
                                Allocation.department   == request.form.get("requester", type=int, default=None), 
                                Allocation.isFinal      == True
                                )



    # getting the name of the user who approves the request
    supervisorID = require_login().supervisor


    # saving the newly approved allocation
    newApprovedAlloc = Allocation.create(termCode       = nextAY.termCode, 
                                        department      = request.form.get("requester", type=int, default=None), 
                                        isFinal         = True,
                                        approvedBy      = supervisorID,
                                        approvedOn      = date.today(),
                                        primary_10      = request.form.get("primary_10", type=int, default=currentAlloc.primary_10),
                                        primary_12      = request.form.get("primary_12", type=int, default=currentAlloc.primary_12),
                                        primary_15      = request.form.get("primary_15", type=int, default=currentAlloc.primary_15),
                                        primary_20      = request.form.get("primary_20", type=int, default=currentAlloc.primary_20),
                                        secondary_5     = request.form.get("secondary_5", type=int, default=currentAlloc.secondary_5),
                                        secondary_10    = request.form.get("secondary_10", type=int, default=currentAlloc.secondary_10),
                                        breakHours      = request.form.get("breakHours", type=int, default=currentAlloc.breakHours)
                                        )
    newApprovedAlloc.save()


    return redirect("/admin/manageDepartments")