from datetime import datetime

from flask import abort, g, jsonify, redirect, render_template, request, send_file, url_for, flash
from peewee import DoesNotExist
from app.login_manager import require_login
from app.controllers.main_routes import main_bp

from app.models.department import Department
from app.models.positionHistory import PositionHistory
from app.models.supervisor import Supervisor
from app.models.supervisorDepartment import SupervisorDepartment

from app.logic.download import makePositionDescriptionPDF
from app.logic.getPositions import getPosition, getPositions, getPositionDescriptionSections
from app.logic.getSupervisors import buildSupervisorDisplay, getSupervisorDepartments
from app.logic.manageMembers import attachPositionCounts, getActivePendingPositionCounts
from app.logic.search import searchPerson
from app.logic.getTerms import getTerms
from app.login_manager import require_login
from app.models.allocation import Allocation
from app.logic.allocationRequest import getOrUpdateRequestedAllocation
from app.logic.allocationManager import allocationExists
from app.logic.academicYearManager import getCurrentAndNextAY

@main_bp.route('/department/<org>/<account>/positions/<positionCode>', methods=['GET'])
def postionDescription(org, account, positionCode):
    try:
        dept = Department.get(Department.ORG == org, Department.ACCOUNT == account)
    except (NameError, DoesNotExist):
        return render_template('errors/404.html'), 404

    revisionDateParam = request.args.get('revisionDate')
    revisionDate = None
    if revisionDateParam:
        try:
            revisionDate = datetime.strptime(revisionDateParam, '%Y-%m-%d').date()
        except ValueError:
            return render_template('errors/404.html'), 404

    position = getPosition(dept, positionCode, revisionDate)

    if not position:
        return render_template('errors/404.html'), 404

    sections = getPositionDescriptionSections(position)

    return render_template(
        'main/individualPositions.html',
        department=dept,
        position=position,
        sections=sections
    )

@main_bp.route('/department/<org>/<account>/positions/<positionCode>/download', methods=['GET'])
def downloadPositionDescription(org, account, positionCode):
    try:
        dept = Department.get(Department.ORG == org, Department.ACCOUNT == account)
    except (NameError, DoesNotExist):
        return render_template('errors/404.html'), 404

    revisionDateParam = request.args.get('revisionDate')
    revisionDate = None
    if revisionDateParam:
        try:
            revisionDate = datetime.strptime(revisionDateParam, '%Y-%m-%d').date()
        except ValueError:
            return render_template('errors/404.html'), 404

    position = getPosition(dept, positionCode, revisionDate)

    if not position:
        return render_template('errors/404.html'), 404

    pdfBuffer = makePositionDescriptionPDF(dept, position)

    filename = f'{position.positionCode}_position_description.pdf'
    return send_file(pdfBuffer, mimetype='application/pdf', as_attachment=True, download_name=filename)

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


@main_bp.route('/department/<org>/<account>/allocations/request', methods=['GET'])
def allocationRequest(org, account):

    # getting the name of the currently chosen department (based on the org and account numbers)
    try:
        dept = Department.get(Department.ORG == org, Department.ACCOUNT == account)
    except DoesNotExist:
        return render_template('errors/404.html'), 404
    

    # checking if the user can visit this page
    if not g.currentUser.isLaborAdmin:
        if not SupervisorDepartment.select().where(
            (SupervisorDepartment.supervisor == g.currentUser.supervisor) &
            (SupervisorDepartment.department == dept.departmentID)
        ).exists():
            return render_template('errors/403.html'), 403
    

    # Retrieving the current and following academic years
    currentAY, nextAY = getCurrentAndNextAY()


    # checking if the allocation has already been approved (in other words, if an approved allocation exists)
    if allocationExists(nextAY.termCode, dept, isFinal=True):
        flash(f"The allocation for the {nextAY.termName.split(' ')[1]} academic year has already been approved; therefore, you can no longer resubmit it.", "info")
        return redirect(f'/department/{org}/{account}')
    

    # getting the current approved allocation
    currentAlloc = Allocation.get_or_none(Allocation.termCode == currentAY.termCode, Allocation.department == dept, Allocation.isFinal == True)


    return render_template('main/allocationRequest.html', 
                            department = dept, 
                            nextAY = nextAY, 
                            currentAlloc = currentAlloc
                            )


@main_bp.route('/allocationRequest/submit', methods=['POST'])
def submitAllocationRequest():  
    getOrUpdateRequestedAllocation()
    submitter = Department.get(Department.departmentID == request.form.get("submitter", type=int, default=None))
    return redirect(f"/department/{submitter.ORG}/{submitter.ACCOUNT}")


@main_bp.route('/members/search/<query>', methods=['GET'])
def searchMember(query=None):
    """Search supervisors by name or B-number."""
    currentUser = g.currentUser

    if not (currentUser.isLaborAdmin or currentUser.isLaborDepartmentStudent or currentUser.supervisor):
        return render_template('errors/403.html'), 403

    supervisorsList = (searchPerson(Supervisor, query).order_by(Supervisor.LAST_NAME.asc()).limit(10))
    supervisorsBuild = [buildSupervisorDisplay(supervisor) for supervisor in supervisorsList]
    supervisorsDisplay = [supervisor for supervisor in supervisorsBuild if supervisor is not None]

    return jsonify(supervisorsDisplay)


@main_bp.route('/members/update_coordinator', methods=['POST'])
def updateCoordinator():
    """Assigns or unassigns a supervisor as a Labor Coordinator."""
    currentUser = g.currentUser

    supervisorID = request.form.get("supervisorID")
    departmentID = request.form.get("departmentID")
    isCoordinator = request.form.get("isCoordinator") == "true"

    if not supervisorID or not departmentID:
        return "", 400

    supervisorDeptRecord = None

    if currentUser.supervisor:
        supervisorDeptRecord = SupervisorDepartment.get_or_none((SupervisorDepartment.supervisor == currentUser.supervisor) & (SupervisorDepartment.department == departmentID))

    if not (currentUser.isLaborAdmin or currentUser.isLaborDepartmentStudent or supervisorDeptRecord):
        return render_template('errors/403.html'), 403

    member = SupervisorDepartment.get((SupervisorDepartment.supervisor == supervisorID) & (SupervisorDepartment.department == departmentID))

    member.isCoordinator = isCoordinator
    member.save()

    return "", 200


@main_bp.route('/members/update_eligibility', methods=['POST'])
def updateEligibility():
    """Updates a supervisor's eligibility status."""
    currentUser = g.currentUser

    if not (currentUser.isLaborAdmin or currentUser.isLaborDepartmentStudent or currentUser.supervisor):
        return render_template('errors/403.html'), 403

    supervisorID = request.form.get("supervisorID")

    if not supervisorID:
        return "", 400

    member = Supervisor.get(Supervisor.ID == supervisorID)
    member.isBanned = not member.isBanned
    member.save()

    return "", 200


@main_bp.route('/members/remove', methods=['DELETE'])
def removeMember():
    """Removes a staff member from a department."""
    currentUser = g.currentUser

    if not ( currentUser.isLaborAdmin or currentUser.isLaborDepartmentStudent or currentUser.supervisor):
        return render_template('errors/403.html'), 403

    supervisorID = request.form.get("supervisorID")
    departmentID = request.form.get("departmentID")

    if not supervisorID or not departmentID:
        return "", 400

    member = SupervisorDepartment.get((SupervisorDepartment.supervisor == supervisorID) & (SupervisorDepartment.department == departmentID))

    member.delete_instance()

    return "", 200


@main_bp.route('/members/add', methods=['POST'])
def addUserToDept():
    """Adds a user to a department."""
    currentUser = g.currentUser
    supervisorID = request.form.get("supervisorID")
    departmentID = request.form.get("departmentID")

    if not supervisorID or not departmentID:
        return jsonify(success=False, message="Missing supervisor or department."), 400

    if not (currentUser.isLaborAdmin or currentUser.isLaborDepartmentStudent or currentUser.supervisor):
        return render_template('errors/403.html'), 403

    try:
        supervisor = Supervisor.get_or_none(Supervisor.ID == supervisorID)

        if not supervisor:
            return jsonify(success=False, message="Supervisor not found."), 404

        supervisorDeptRecord = SupervisorDepartment.get_or_none( supervisor=supervisor, department=departmentID )

        if supervisorDeptRecord:
            return jsonify(
                success=False,
                message="Supervisor already exists in this department."
            ), 200

        SupervisorDepartment.create( supervisor=supervisor, department=departmentID)

        return jsonify(success=True, message="Supervisor added to department."), 200

    except Exception as e:
        print(f'Could not add user to department: {e}')
        return jsonify(
            success=False,
            message="Could not add supervisor to department."
        ), 500
        
@main_bp.route('/department/<org>/<account>/members', methods=['GET'])
def manageMembers(org=None, account=None):
    """Generates the Manage Members page."""
    currentUser = g.currentUser

    if not currentUser.supervisor:
        return redirect(url_for('main.laborhistory', id=currentUser.student.ID))

    dept = Department.get_or_none(Department.ORG == org, Department.ACCOUNT == account)

    if not dept:
        abort(404)

    departmentMembers = getSupervisorDepartments(dept)
    supervisorDeptRecord = SupervisorDepartment.get_or_none(supervisor=currentUser.supervisor, department=dept)

    if not ( currentUser.isLaborAdmin or currentUser.isLaborDepartmentStudent or supervisorDeptRecord):
        return render_template('errors/403.html'), 403

    currentTerms = getTerms()

    activePendingPositionCounts = getActivePendingPositionCounts(dept, currentTerms)
    departmentMembers = attachPositionCounts(departmentMembers, activePendingPositionCounts)

    return render_template(
        'main/manageMembers.html',
        members = departmentMembers,
        currentUser = currentUser,
        department = dept,
        academicYear = currentTerms[0],
    )