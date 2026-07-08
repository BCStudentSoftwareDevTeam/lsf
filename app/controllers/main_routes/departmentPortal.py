from flask import render_template, request, json, redirect, url_for, send_file, g, flash, jsonify
from peewee import JOIN, DoesNotExist, fn, Case
from functools import reduce
import operator
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

