from datetime import datetime

from flask import g, render_template, request, send_file, redirect, flash
from peewee import DoesNotExist
from app.login_manager import require_login
from app.controllers.main_routes import main_bp
from app.logic.download import makePositionDescriptionPDF
from app.logic.getPositions import getPosition, getPositions, getPositionDescriptionSections
from app.models.department import Department
from app.models.positionHistory import PositionHistory
from app.models.allocation import Allocation
from app.models.supervisorDepartment import SupervisorDepartment

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
