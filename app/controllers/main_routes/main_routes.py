from flask import render_template, request, json, redirect, url_for, send_file, g, flash, jsonify
from peewee import JOIN, DoesNotExist
from functools import reduce
import operator
from app.models.department import Department
from app.models.supervisor import Supervisor
from app.models.supervisorDepartment import SupervisorDepartment
from app.models.student import Student
from app.models.formHistory import FormHistory
from app.controllers.admin_routes.allPendingForms import checkAdjustment
from app.controllers.main_routes import main_bp
from app.logic.download import CSVMaker, saveFormSearchResult, retrieveFormSearchResult
from app.logic.search import getDepartmentsForSupervisor, searchPerson, searchSupervisorPortal
from app.login_manager import require_login, logout
from app.logic.getTableData import getDatatableData
from app.logic.banner import Banner
from app.logic.tracy import Tracy
from app.logic.allocation import getAllocationSummary
from app.models.positionHistory import PositionHistory
from app.logic.getPositions import getActivePositions

@main_bp.route('/logout', methods=['GET'])
def triggerLogout():
    return redirect(logout())

@main_bp.route('/', methods=['GET', 'POST'])
def supervisorPortal():
    '''
    When the request is GET the function populates the General Search interface dropdown menus with their corresponding values.
    If the request is POST it also populates the datatable with data based on S input.
    '''
    currentUser = require_login()
    if not currentUser or not currentUser.supervisor:
        if currentUser.student:
            return redirect(url_for('main.laborhistory',id=currentUser.student.ID))

        return render_template('errors/403.html'), 403
    
    if request.method == 'POST':
        return getDatatableData(request)
    
    if currentUser.isLaborAdmin or currentUser.isFinancialAidAdmin or currentUser.isSaasAdmin:
        departments = list(Department.select().order_by(Department.isActive.desc(), Department.DEPT_NAME.asc()))
    else:
        departments = list(getDepartmentsForSupervisor(currentUser).order_by(Department.isActive.desc(), Department.DEPT_NAME.asc()))

    return render_template('main/supervisorPortal.html',
                            departments = departments,
                            currentUser = currentUser
                            )

@main_bp.route('/department', methods=['GET'])
@main_bp.route('/department/<org>', methods=['GET'])
@main_bp.route('/department/<org>/<account>', methods=['GET'])
def departmentPortal(org=None,account=None):
    try:
        dept = Department.get(Department.ORG == org, Department.ACCOUNT == account)
    except (NameError, DoesNotExist):
        dept = None


    if g.currentUser.isLaborAdmin:
        departments = list(Department.select().order_by(Department.isActive.desc(), Department.DEPT_NAME.asc()))
    else:
        departments = list(getDepartmentsForSupervisor(g.currentUser).order_by(Department.isActive.desc(), Department.DEPT_NAME.asc()))

    staff = Tracy().getSupervisors()
    supervisors = []

    for i in staff:
        if i.ORG == org:
            supervisors.append(i.FIRST_NAME + " " + i.LAST_NAME + " (" + i.EMAIL + ")")

    allocationSummary = getAllocationSummary(dept, g.openTerm)
    positionsList, posURL = getActivePositions(dept)

    return render_template('main/departmentPortal.html',
                           departments = departments,
                           department = dept,
                           positions = positionsList,
                           posURL = posURL,
                           supervisors = supervisors,
                           allocation = allocationSummary['allocation'],
                           allocationBands = allocationSummary['allocationBands'],
                           totalPositionsAllocated = allocationSummary['totalPositionsAllocated'],
                           totalPositionsUsed = allocationSummary['totalPositionsUsed'],
                           breakHoursUsed = allocationSummary['breakHoursUsed'],
                           currentTerm = g.openTerm)

@main_bp.route('/supervisorPortal/addUserToDept', methods=['GET', 'POST'])
def addUserToDept():
    userDeptData = request.form
    supervisorDeptRecord = SupervisorDepartment.get_or_none(supervisor = userDeptData['supervisorID'], department = userDeptData['departmentID'])
    try:
        if supervisorDeptRecord:
            return "False"

        else:
            SupervisorDepartment.create(supervisor=userDeptData['supervisorID'], department=userDeptData['departmentID'])
            return "True"
    
    except Exception as e:
        print(f'Could not add user to department: {e}')
        return "", 500

@main_bp.route('/supervisorPortal/download', methods=['POST'])
def downloadSupervisorPortalResults():
    '''
    This function uses the general search results, stored in a global variable, to
    generate a CSV file of datatable data.
    '''
    formSearchResults = retrieveFormSearchResult(request.form.get('downloadId'))
    if not formSearchResults:
        print(f"[ERROR] Missing or invalid download ID for form search.")
        return "", 500

    formSearchResultIds = json.loads(formSearchResults.formHistoryIds)
    formHistories = FormHistory.select().where(FormHistory.formHistoryID.in_(formSearchResultIds)).order_by(-FormHistory.createdDate)
    excel = CSVMaker(
        formSearchResults.searchType,
        requestedLSFs=formHistories, 
        additionalSpreadsheetFields=[],
        includeEvals=False
    )
    return send_file(excel.relativePath, as_attachment=True, attachment_filename=excel.relativePath.split('/').pop())

@main_bp.route('/supervisorPortal/liveSearch', methods=['GET'])
def SupervisorPortalSearch():
    """
    Returns a list of users that match a given string
    """
    searchType = request.args.get("searchType")
    userInput = request.args.get("userInput")

    if not searchType or not userInput:
        return jsonify({}), 400
    currentUser = require_login()
    userList = searchSupervisorPortal(currentUser, searchType, userInput)
    return jsonify(userList)

@main_bp.route('/lsf/<formHistoryId>/submitToBanner', methods=['GET']) 
def submitToBanner(formHistoryId):
    if not (g.currentUser.isLaborAdmin or g.currentUser.isLaborDepartmentStudent):
        return render_template('errors/403.html'), 403      

    try:
        conn = Banner()
        save_form_status = conn.insert(formHistoryId)
    except Exception as e:
        save_form_status = False
        print(f"Error saving form history ({formHistoryId}) to Banner.")

    if save_form_status:
        return "Form successfully submitted to Banner.", 200
    else:
        return "Submitting to Banner failed.", 500
