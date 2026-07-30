from flask import render_template, g
from peewee import DoesNotExist

from app.models.department import Department
from app.models.allocation import Allocation
from app.models.laborStatusForm import LaborStatusForm
from app.models.formHistory import formHistory

from app.controllers.main_routes import main_bp

@main_bp.route('/department/<org>/<account>/allocations', methods=['GET'])
def allocationTable(org=None, account=None):
    currentUser = g.currentUser
    try:
        dept = Department.get(Department.ORG == org, Department.ACCOUNT == account)
    except (NameError, DoesNotExist):
        dept = None

    return render_template('main/')