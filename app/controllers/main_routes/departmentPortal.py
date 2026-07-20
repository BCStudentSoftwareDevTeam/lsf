import re
from datetime import date
from flask import render_template, request, json, redirect, session, url_for, send_file, g, flash, jsonify
from peewee import JOIN, DoesNotExist, fn, Case
from functools import reduce
import operator
from app.logic.userInsertFunctions import createSupervisorFromTracy
from app.models.department import Department
from app.models.supervisor import Supervisor
from app.models.supervisorDepartment import SupervisorDepartment
from app.models.student import Student
from app.models.laborStatusForm import LaborStatusForm
from app.models.formHistory import FormHistory
from app.models.laborReleaseForm import LaborReleaseForm
from app.models.term import Term
from app.controllers.admin_routes.allPendingForms import checkAdjustment
from app.controllers.main_routes import main_bp
from app.logic.download import CSVMaker, saveFormSearchResult, retrieveFormSearchResult
from app.logic.search import getDepartmentsForSupervisor, searchPerson, searchSupervisorPortal
from app.login_manager import require_login, logout
from app.logic.getTableData import getDatatableData
from app.logic.banner import Banner
from flask import abort
from app.logic.search import limitSearchByUserDepartment, studentDbToDict, usernameFromEmail



@main_bp.route('/department/<org>/<account>/members', methods=['GET'])
def manageMembers(org=None,account=None):
    """
    Generates the Manage Members page.
    """
    currentUser = require_login()
    currentSupervisor = Supervisor.select().where(Supervisor.ID == currentUser.supervisor).get()
    if not currentUser or not currentUser.supervisor:
        if currentUser.student:
            return redirect(url_for('main.laborhistory',id=currentUser.student.ID))

        return render_template('errors/403.html'), 403
    
    try:
        dept = Department.get(Department.ORG == org, Department.ACCOUNT == account)
        session['current_department_id'] = dept.departmentID
        session['current_department'] = dept.DEPT_NAME
    except (NameError, DoesNotExist):
        dept = None
        abort(404)

    members = list( SupervisorDepartment.select(SupervisorDepartment,Supervisor).where(SupervisorDepartment.department == dept).join(Supervisor).dicts())

    today = date.today()
    releasedForms = (FormHistory.select(FormHistory.formID).join(LaborReleaseForm)
        .where(
            (FormHistory.historyType == "Labor Release Form") &
            (FormHistory.status == "Approved") &
            (LaborReleaseForm.releaseDate <= today)
        )
    )

    # Finding the current academic year
    currentYear = today.year
    if today.month < 7: 
        currentAcademicYear = (currentYear - 1, currentYear)
    else: 
        currentAcademicYear = (currentYear, currentYear + 1)
    # Note that the start of July is 
    # normally considered the start of a new academic year.

    
    # Conditions used for the studentCount variable
    activePrimaries = (
        (LaborStatusForm.jobType == 'Primary') &
        (LaborStatusForm.studentConfirmation == True))
    pendingPrimaries = (
        (LaborStatusForm.jobType == 'Primary') &
        (LaborStatusForm.studentConfirmation.is_null(True)))
    activeSecondaries = (
        (LaborStatusForm.jobType == 'Secondary') &
        (LaborStatusForm.studentConfirmation == True))
    pendingSecondaries = (
        (LaborStatusForm.jobType == 'Secondary') &
        (LaborStatusForm.studentConfirmation.is_null(True)))


    # This variable is used for the Supervisees column on the
    # Manage Members page.  
    studentCount = list(
        LaborStatusForm.
        select(
            fn.SUM(Case(None, ((activePrimaries, 1),), 0)).alias("active_primary_positions"), 
            fn.SUM(Case(None, ((pendingPrimaries, 1),), 0)).alias("pending_primary_positions"), 
            fn.SUM(Case(None, ((activeSecondaries, 1),), 0)).alias("active_secondary_positions"),
            fn.SUM(Case(None, ((pendingSecondaries, 1),), 0)).alias("pending_secondary_positions"),
            LaborStatusForm.department, 
            LaborStatusForm.supervisor
        ).where(
            # Expired and released positions are not counted! 
            (LaborStatusForm.department == dept) &
            (LaborStatusForm.laborStatusFormID.not_in(releasedForms))
        ).group_by(
            LaborStatusForm.department, 
            LaborStatusForm.supervisor
        ).dicts()
    )


    counts = {(row["department"], row["supervisor"]): row for row in studentCount}
    for member in members:

        key = (member["department"], member["supervisor"])
        row = counts.get(key, {})

        member["active_primary_positions"]      = row.get("active_primary_positions", 0)
        member["pending_primary_positions"]     = row.get("pending_primary_positions", 0)
        member["active_secondary_positions"]    = row.get("active_secondary_positions", 0)
        member["pending_secondary_positions"]   = row.get("pending_secondary_positions", 0)

    return render_template('main/manageMembers.html', 
                           members = members,
                           department = dept, 
                           currentSupervisor= currentSupervisor,
                           currentAcademicYear = currentAcademicYear)



def supervisorsDbToDict(supervisor):
    """
    Given a supervisor object it will return a mapped Dict with supervisor data.
    """
    dbToDict =  {'username': usernameFromEmail(supervisor.EMAIL.strip()),
                'firstName': supervisor.FIRST_NAME.strip(),
                'lastName': supervisor.LAST_NAME.strip(),
                'bnumber': supervisor.ID.strip(),
                'department': supervisor.DEPT_NAME.strip(),
                'type': 'Supervisor'}
    return dbToDict



@main_bp.route('/members/search/<query>',  methods=['GET'])
def searchMember(query=None):
    """
    Search student table and STUDATA for student results.
    """
    currentUser = require_login()
    accessAllowed = currentUser and (currentUser.supervisor or currentUser.isLaborAdmin)
    if not accessAllowed:
        return render_template('errors/403.html'), 403

    recordedSupervisors = []  # supervisors recorded in the database
    query = query.strip()

    displayedSupervisors = Supervisor.select()

    # bnumber search
    if re.match(r'[Bb]\d+', query):
        recordedSupervisors = list(map(supervisorsDbToDict, displayedSupervisors.where(Supervisor.ID % "{}%".format(query.upper()))))
        

    # name search
    else:
        if " " not in query:
            search = query.upper() + "%"
            results = displayedSupervisors.where(Supervisor.preferred_name ** search | Supervisor.legal_name ** search | Supervisor.LAST_NAME ** search)
        else:
            search = query.upper().split()
            firstQuery = search[0] + "%"
            lastQuery = search[-1] + "%"
            results = displayedSupervisors.where((Supervisor.preferred_name ** firstQuery | Supervisor.legal_name ** firstQuery) & Supervisor.LAST_NAME ** lastQuery)

        recordedSupervisors = list(map(supervisorsDbToDict, results))
        

    # combine lists, remove duplicates, and then sort
    supervisors = list({v['bnumber']:v for v in (recordedSupervisors)}.values())
    supervisors = sorted(supervisors, key=lambda f: f['firstName'] + f['lastName'])

    return jsonify(supervisors)

@main_bp.route('/members/coordinator_switch', methods=['POST'])
def coordinatorSwitch():
    """
    Assigns or unassignes a supervisor as a Labor Coordinator. 
    """
    data = request.get_json()
    supervisorID = data.get("supervisorID")
    isCoordinator = data.get("isCoordinator")

    member = SupervisorDepartment.get(SupervisorDepartment.supervisor == supervisorID)
    member.isCoordinator = isCoordinator
    member.save()

    return "", 200


@main_bp.route('/members/ban_switch', methods=['POST'])
def elegibilitySwitch():
    """
    Updates a supervisor's eligibility status. 
    """
    data = request.get_json()
    supervisorID = data.get("supervisorID")

    member = Supervisor.get(Supervisor.ID == supervisorID)
    
    member.isBanned = not member.isBanned
    member.save()

    return "", 200


@main_bp.route('/members/remove', methods=['DELETE'])
def removeMember():
    """
    Removes a staff member from a department. 
    """
    data = request.get_json()
    supervisorID = data.get("supervisorID")
    
    member = SupervisorDepartment.get(
        (SupervisorDepartment.supervisor == supervisorID) &
        (SupervisorDepartment.department == session['current_department_id'])
        )
    member.delete_instance()

    return "", 200



@main_bp.route('/members/add', methods=['GET', 'POST'])
def addUserToDept():
    """
    Adds a user to a department.
    """
    userDeptData = request.form
    supervisorDeptRecord = SupervisorDepartment.get_or_none(supervisor = userDeptData['supervisorID'], department = userDeptData['departmentID'])
    try:
        if supervisorDeptRecord:
            return "False"

        else:
            supervisorID = userDeptData['supervisorID']
            if not Supervisor.get_or_none(Supervisor.ID == supervisorID):
                createSupervisorFromTracy(bnumber=supervisorID)

            SupervisorDepartment.create(supervisor=supervisorID, department=userDeptData['departmentID'])
            return "True"
    
    except Exception as e:
        print(f'Could not add user to department: {e}')
        return "", 500