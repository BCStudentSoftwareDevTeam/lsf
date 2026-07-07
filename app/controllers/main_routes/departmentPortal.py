from flask import render_template, request, json, redirect, url_for, send_file, g, flash, jsonify
from peewee import JOIN, DoesNotExist
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

    members = list(SupervisorDepartment.select(SupervisorDepartment, Supervisor).where(SupervisorDepartment.department == dept).join(Supervisor).order_by(SupervisorDepartment.isActive.desc()).dicts())

    return render_template('main/manageMembers.html', 
                           members = members,
                           department = dept)

