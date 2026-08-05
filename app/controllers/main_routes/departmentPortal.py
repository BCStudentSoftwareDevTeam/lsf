from flask import render_template, g, request, redirect, flash
from app.login_manager import require_login
from app.controllers.main_routes import main_bp
from app.logic.getPositions import getPositions
from peewee import DoesNotExist
from app.models.department import Department
from app.models.allocation import Allocation
from app.models.supervisorDepartment import SupervisorDepartment
from app.logic.allocationRequest import getOrUpdateRequestedAllocation
from app.logic.allocationManager import allocationExists
from app.logic.academicYearManager import getCurrentAndNextAY


@main_bp.route('/department/<org>/<account>/allocations/request', methods=['GET'])
def allocationRequest(org, account):

    # getting the name of the currently chosen department (based on the org and account numbers)
    try:
        dept = Department.get(Department.ORG == org, Department.ACCOUNT == account)
    except DoesNotExist:
        return render_template('errors/404.html'), 404
    

    # cheching if the user can visit this page
    if not g.currentUser.isLaborAdmin:
        if not SupervisorDepartment.select().where(
            (SupervisorDepartment.supervisor == g.currentUser.supervisor) &
            (SupervisorDepartment.department == dept.departmentID)
        ).exists():
            return render_template('errors/403.html'), 403
    

    # Retrieving the current and following academic years 
    # DON'T DELETE THE UNDERSCORES
    currentAY, nextAY = getCurrentAndNextAY()


    # checking if the allocation has already been approved (in other words, if an approved allocation exists)
    if allocationExists(nextAY.termCode, dept, isFinal=True):
        flash(f"The allocation for the {nextAY.termName.split(" ")[1]} academic year has already been approved; therefore, you can no longer resubmit it.", "danger")
        return redirect('/admin/manageDepartments/')
    

    # getting the current approved allocation
    currentAlloc = Allocation.get(Allocation.termCode == currentAY.termCode, Allocation.department == dept, Allocation.isFinal == True)


    return render_template('main/allocationRequest.html', 
                            department = dept, 
                            nextAY = nextAY, 
                            currentAlloc = currentAlloc
                            )


@main_bp.route('/allocationRequest/submit', methods=['POST'])
def submitAllocationRequest():  
    getOrUpdateRequestedAllocation()
    return redirect("/admin/manageDepartments")


@main_bp.route('/department/<org>/<account>/positions', methods=['GET'])
def managePositions(org, account):
    try:
        dept = Department.get(Department.ORG == org, Department.ACCOUNT == account)
    except DoesNotExist:
        return render_template('errors/404.html'), 404
    
    if not g.currentUser.isLaborAdmin:
        if not SupervisorDepartment.select().where(
            (SupervisorDepartment.supervisor == g.currentUser.supervisor) &
            (SupervisorDepartment.department == dept.departmentID)
        ).exists():
            return render_template('errors/403.html'), 403

    positions = getPositions(dept)

    return render_template('main/managePositions.html',
                           department = dept,
                           department_name = dept.DEPT_NAME,
                           positions = positions
                           )
