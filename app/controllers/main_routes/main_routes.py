from flask import render_template, request, json, redirect, url_for, send_file, g, flash, jsonify
from peewee import JOIN, DoesNotExist, fn
from functools import reduce
from datetime import datetime, date
import operator

from app.models.department import Department
from app.models.supervisor import Supervisor
from app.models.supervisorDepartment import SupervisorDepartment
from app.models.student import Student
from app.models.laborStatusForm import LaborStatusForm
from app.models.formHistory import FormHistory
from app.models.term import Term
from app.models.positionHistory import PositionHistory
from app.models.allocation import Allocation

from app.controllers.admin_routes.allPendingForms import checkAdjustment
from app.controllers.main_routes import main_bp

from app.logic.download import CSVMaker, saveFormSearchResult, retrieveFormSearchResult
from app.logic.search import getDepartmentsForSupervisor, searchPerson, searchSupervisorPortal
from app.login_manager import require_login, logout
from app.logic.getTableData import getDatatableData
from app.logic.banner import Banner
from app.logic.getSupervisors import getSupervisors
from app.logic.getPositions import getActivePositions
from app.logic.allocationManager import *



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
    currentUser = g.currentUser
    try:
        dept = Department.get(Department.ORG == org, Department.ACCOUNT == account)
    except (NameError, DoesNotExist):
        dept = None

    if currentUser.isLaborAdmin:
        departments = list(Department.select().order_by(Department.isActive.desc(), Department.DEPT_NAME.asc()))
    else:
        departments = list(Department.select().join(SupervisorDepartment).where(SupervisorDepartment.supervisor == currentUser.supervisor).order_by(Department.isActive.desc(), Department.DEPT_NAME.asc()))
    
    supervisors, laborCoordinators = getSupervisors(dept)

    positionsList, posURL = getActivePositions(dept) 

    return render_template('main/departmentPortal.html', 
                           departments = departments,
                           department = dept,
                           supervisors = supervisors,
                           laborCoordinators=laborCoordinators,
                           currentUser=currentUser,
                           positions = positionsList,
                           posURL = posURL)

@main_bp.route('/department/<org>/<account>/allocations', methods=['GET'])
def allocationTable(org=None, account=None):
    currentUser = g.currentUser
    try:
        dept = Department.get(Department.ORG == org, Department.ACCOUNT == account)
    except (NameError, DoesNotExist):
        dept = None

    if currentUser.isLaborAdmin:
        pass
    else:
        departments = list(Department.select().join(SupervisorDepartment).where(SupervisorDepartment.supervisor == currentUser.supervisor).order_by(Department.isActive.desc(), Department.DEPT_NAME.asc()))

    currentDate = str(date.today())
    if int(currentDate[5:7]) <= 6:
        # If it is the spring semester, then the term code is 1 year behind. e.g. 2025-2026 term code is 202500.
        springTerm = Term.select().where(Term.termCode == int(currentDate[:4] + "12") - 100).get()
        currentAY = currentTerm = Term.select().where(Term.termCode == int(currentDate[:4] + "00") - 100).get()
        fallTerm = Term.select().where(Term.termCode == int(currentDate[:4] + "11") - 100).get()

    else:
        fallTerm = Term.select().where(Term.termCode == currentDate[:4] + "11").get()
        currentAY = Term.select().where(Term.termCode == currentDate[:4] + "00").get()
        springTerm = Term.select().where(Term.termCode == currentDate[:4] + "12").get()


    allocationDict = {"primary_10": 1,
                    "primary_12": 2,
                    "primary_15": 3,
                    "primary_20": 4,
                    "secondary_5": 5,
                    "secondary_10": 6,
                    "breakHours": 500,
                    "totalPrimaries": 10,
                    "totalSecondaries": 11,
                    "totalAllocations": 21}
    fallContracts = getContractedAllocations(fallTerm, dept)
    springContracts = getContractedAllocations(springTerm, dept)

    breakContracts = {
        "thanksgiving":getBreakContracts(currentAY.termCode + 1, dept),
        "winter": getBreakContracts(currentAY.termCode + 2, dept),
        "spring": getBreakContracts(currentAY.termCode + 3, dept),
        "fall":getBreakContracts(currentAY.termCode + 4, dept),
        "summer": getBreakContracts(currentAY.termCode + 13, dept)
        }
     
    return render_template('main/allocationTable.html',
                           department = dept,
                           currentAY = currentAY,
                           allocations = allocationDict,
                           fallContracts = fallContracts,
                           springContracts = springContracts,
                           breakContracts = breakContracts)
                           

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
