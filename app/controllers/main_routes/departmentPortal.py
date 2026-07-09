import re

from flask import render_template, request, json, redirect, url_for, send_file, g, flash, jsonify
from peewee import JOIN, DoesNotExist, fn, Case
from functools import reduce
import operator
from app.logic.tracy import Tracy
from app.models.department import Department
from app.models.supervisor import Supervisor
from app.models.supervisorDepartment import SupervisorDepartment
from app.models.student import Student
from app.models.laborStatusForm import LaborStatusForm
from app.models.formHistory import FormHistory
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
    except (NameError, DoesNotExist):
        dept = None
        abort(404)

    members = list(
        SupervisorDepartment.
        select(
            SupervisorDepartment,
            Supervisor
        ).where(
            SupervisorDepartment.department == dept
        ).join(
            Supervisor
        ).dicts()
    )

    student_count = list(
        LaborStatusForm.
        select(
            fn.SUM(Case(LaborStatusForm.jobType, (("Primary", 1),), 0)).alias("primary_positions"), 
            fn.SUM(Case(LaborStatusForm.jobType, (("Secondary", 1),), 0)).alias("secondary_positions"),
            LaborStatusForm.department, 
            LaborStatusForm.supervisor
        ).group_by(
            LaborStatusForm.department, 
            LaborStatusForm.supervisor
        ).dicts()
    )

    
    counts = {(row["department"], row["supervisor"]): row for row in student_count}
    
    for member in members:

        key = (member["department"], member["supervisor"])
        row = counts.get(key, {})

        member["primary_positions"] = row.get("primary_positions", 0)
        member["secondary_positions"] = row.get("secondary_positions", 0)

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
                'type': 'Supervisor'}
    return dbToDict

# search student table and STUDATA for student results
@main_bp.route('/members/search/<query>',  methods=['GET'])
def add_member(query=None):
    currentUser = require_login()
    accessAllowed = currentUser and (currentUser.supervisor or currentUser.isLaborAdmin)
    if not accessAllowed:
        return render_template('errors/403.html'), 403

    current_supervisors = []
    our_supervisors = []
    query = query.strip()

    # bnumber search
    if re.match('[Bb]\d+', query):
        our_supervisors = list(map(supervisorsDbToDict, Supervisor.select().where(Supervisor.ID % "{}%".format(query.upper()))))
        current_supervisors = list(map(supervisorsDbToDict, Tracy().getSupervisorsFromBNumberSearch(query)))

    # name search
    else:
        if " " not in query:
            search = query.upper() + "%"
            results = Supervisor.select().where(Supervisor.preferred_name ** search | Supervisor.legal_name ** search | Supervisor.LAST_NAME ** search)
        else:
            search = query.upper().split()
            first_query = search[0] + "%"
            last_query = search[-1] + "%"
            results = Supervisor.select().where((Supervisor.preferred_name ** first_query | Supervisor.legal_name ** first_query) & Supervisor.LAST_NAME ** last_query)

        our_supervisors = list(map(supervisorsDbToDict, results))
        current_supervisors = list(map(supervisorsDbToDict, Tracy().getSupervisorsFromUserInput(query)))

    # combine lists, remove duplicates, and then sort
    supervisors = list({v['bnumber']:v for v in (current_supervisors + our_supervisors)}.values())
    supervisors = sorted(supervisors, key=lambda f:f['firstName'] + f['lastName'])

    return jsonify(supervisors)
