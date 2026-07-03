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

@main_bp.route('/department/manage_staff', methods=['GET'])
@main_bp.route('/department/manage_staff/<org>', methods=['GET'])
@main_bp.route('/department/manage_staff/<org>/<account>', methods=['GET'])
def manageStaff(org=None,account=None):
    try:
        dept = Department.get(Department.ORG == org, Department.ACCOUNT == account)
    except (NameError, DoesNotExist):
        dept = None



    if g.currentUser.isLaborAdmin:
        departments = list(Department.select().order_by(Department.isActive.desc(), Department.DEPT_NAME.asc()))
    else:
        departments = list(getDepartmentsForSupervisor(g.currentUser).order_by(Department.isActive.desc(), Department.DEPT_NAME.asc()))

    labor = [["Scott Heggen", 7, 11, 0, 1, "B0010201"], ["Brian Ramsay", 9, 12, 0, 1, "B0011251"], ["Bright Feitsop", 10, 20, 1, 0, "B023241"], ["Artem Kurasov", 6, 7, 0, 0, "B1110201"]]

    return render_template('main/manageStaff.html', 
                           staff = labor,
                           department = "Computer Science")

