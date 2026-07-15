import re
from datetime import date
from flask import render_template, request, json, redirect, session, url_for, send_file, g, flash, jsonify
from peewee import JOIN, DoesNotExist, fn, Case
from functools import reduce
import operator
from app.logic.tracy import Tracy
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
def manageStaff(org=None,account=None):
    try:
        dept = Department.get(Department.ORG == org, Department.ACCOUNT == account)
        session['current_department_id'] = dept.departmentID
        session['current_department'] = dept.DEPT_NAME
    except (NameError, DoesNotExist):
        dept = None
        abort(404)

    members = list( SupervisorDepartment.select(SupervisorDepartment,Supervisor).where(SupervisorDepartment.department == dept).join(Supervisor).dicts())

    today = date.today()
    released_forms = (FormHistory.select(FormHistory.formID).join(LaborReleaseForm)
        .where(
            (FormHistory.historyType == "Labor Release Form") &
            (FormHistory.status == "Approved") &
            (LaborReleaseForm.releaseDate <= today)
        )
    )

    # Conditions for the supervisee counts. Expired and released positions do
    # not contribute to any of the four totals.
    active_primaries = (
        (LaborStatusForm.jobType == 'Primary') &
        (LaborStatusForm.studentConfirmation == True))
    pending_primaries = (
        (LaborStatusForm.jobType == 'Primary') &
        (LaborStatusForm.studentConfirmation.is_null(True)))
    active_secondaries = (
        (LaborStatusForm.jobType == 'Secondary') &
        (LaborStatusForm.studentConfirmation == True))
    pending_secondaries = (
        (LaborStatusForm.jobType == 'Secondary') &
        (LaborStatusForm.studentConfirmation.is_null(True)))


    student_count = list(
        LaborStatusForm.
        select(
            fn.SUM(Case(None, ((active_primaries, 1),), 0)).alias("active_primary_positions"), 
            fn.SUM(Case(None, ((pending_primaries, 1),), 0)).alias("pending_primary_positions"), 
            fn.SUM(Case(None, ((active_secondaries, 1),), 0)).alias("active_secondary_positions"),
            fn.SUM(Case(None, ((pending_secondaries, 1),), 0)).alias("pending_secondary_positions"),
            LaborStatusForm.department, 
            LaborStatusForm.supervisor
        ).where(
            (LaborStatusForm.department == dept) &
            (LaborStatusForm.laborStatusFormID.not_in(released_forms))
        ).group_by(
            LaborStatusForm.department, 
            LaborStatusForm.supervisor
        ).dicts()
    )
    
    counts = {(row["department"], row["supervisor"]): row for row in student_count}
    
    for member in members:

        key = (member["department"], member["supervisor"])
        row = counts.get(key, {})

        member["active_primary_positions"]      = row.get("active_primary_positions", 0)
        member["pending_primary_positions"]     = row.get("pending_primary_positions", 0)
        member["active_secondary_positions"]    = row.get("active_secondary_positions", 0)
        member["pending_secondary_positions"]   = row.get("pending_secondary_positions", 0)

    return render_template('main/manageMembers.html', 
                           members = members,
                           department = dept)


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


# search student table and STUDATA for student results
@main_bp.route('/members/search/<query>',  methods=['GET'])
def searchMember(query=None):
    currentUser = require_login()
    accessAllowed = currentUser and (currentUser.supervisor or currentUser.isLaborAdmin)
    if not accessAllowed:
        return render_template('errors/403.html'), 403

    recordedSupervisors = []  # supervisors recorded in the database
    currentSupervisors = []   # supervisors from Tracy
    query = query.strip()

    currentDepartment = session.get('current_department')
    displayedSupervisors = Supervisor.select()#.where(~fn.EXISTS(SupervisorDepartment.select().where((SupervisorDepartment.supervisor == Supervisor.ID) & (SupervisorDepartment.department != currentDepartment))))

    # bnumber search
    if re.match(r'[Bb]\d+', query):
        recordedSupervisors = list(map(supervisorsDbToDict, displayedSupervisors.where(Supervisor.ID % "{}%".format(query.upper()))))
        currentSupervisors = [
            s for s in map(supervisorsDbToDict, Tracy().getSupervisorsFromUserInput(query))
            if s.get('department') != currentDepartment
        ]


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
        currentSupervisors = [
            s for s in map(supervisorsDbToDict, Tracy().getSupervisorsFromUserInput(query))
            if s.get('department') != currentDepartment
        ]

    # combine lists, remove duplicates, and then sort
    supervisors = list({v['bnumber']:v for v in (currentSupervisors + recordedSupervisors)}.values())
    supervisors = sorted(supervisors, key=lambda f: f['firstName'] + f['lastName'])

    return jsonify(supervisors)

@main_bp.route('/members/coordinator_switch', methods=['POST'])
def coordinator_switch():
    data = request.get_json()
    supervisor_id = data.get("supervisorID")
    is_coordinator = data.get("isCoordinator")

    member = SupervisorDepartment.get(SupervisorDepartment.supervisor == supervisor_id)
    member.isCoordinator = is_coordinator
    member.save()

    return "", 200


@main_bp.route('/members/ban_switch', methods=['POST'])
def ban_switch():
    data = request.get_json()
    supervisor_id = data.get("supervisorID")

    member = Supervisor.get(Supervisor.ID == supervisor_id)
    
    member.isBanned = not member.isBanned
    member.save()

    return "", 200


@main_bp.route('/members/remove', methods=['DELETE'])
def remove_member():
    data = request.get_json()
    supervisor_id = data.get("supervisorID")
    
    member = SupervisorDepartment.get(
        (SupervisorDepartment.supervisor == supervisor_id) &
        (SupervisorDepartment.department == session['current_department_id'])
        )
    member.delete_instance()

    return "", 200



@main_bp.route('/members/add', methods=['GET', 'POST'])
def addUserToDept():
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