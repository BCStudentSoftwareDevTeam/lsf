from flask import render_template, request, json, redirect, url_for, send_file, g, flash, jsonify
from flask_bootstrap import forms
from peewee import JOIN, DoesNotExist, fn
from functools import reduce
import operator
from app.models.allocation import Allocation
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
from app.logic.tracy import Tracy
from app.logic.userInsertFunctions import createSupervisorFromTracy
from app.logic.allocationManager import *
from app.models.positionHistory import PositionHistory


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
    if org and account:
        try:
            dept = Department.get(Department.ORG == org, Department.ACCOUNT == account)
        except (NameError, DoesNotExist):
            dept = None
    else:
        dept = None

    if g.currentUser.isLaborAdmin:
        departments = list(Department.select().order_by(Department.isActive.desc(), Department.DEPT_NAME.asc()))
    else:
        departments = list(getDepartmentsForSupervisor(g.currentUser).order_by(Department.isActive.desc(), Department.DEPT_NAME.asc()))
     
    try:
        allocation = Allocation.select(Allocation, Term).join(Term).where(Allocation.department == dept, Allocation.termCode == 202500).get()
    except DoesNotExist:
        allocation = None
    
    supervisorDepartments = (SupervisorDepartment.select().join(Supervisor).where(SupervisorDepartment.department == dept)
        .order_by(fn.COALESCE(Supervisor.preferred_name, Supervisor.legal_name, Supervisor.LAST_NAME).asc()))

    laborCoordinators = []
    supervisors = []

    for supervisorDepartment in supervisorDepartments:
        supervisor = supervisorDepartment.supervisor

        if supervisor is None:
            continue

        firstName = supervisor.preferred_name or supervisor.legal_name or ""
        lastName = supervisor.LAST_NAME or ""

        supervisorName = f"{firstName} {lastName}".strip()

        supervisorDisplay = {
            "name": supervisorName,
            "email": supervisor.EMAIL
        }

        if supervisorDepartment.isCoordinator:
            laborCoordinators.append(supervisorDisplay)
        else:
            supervisors.append(supervisorDisplay)
    
#     ViewAllocations(org, account)
#     totalPositions = Allocation.select(fn.SUM(Allocation.primary_10) + fn.SUM(Allocation.primary_12) + fn.SUM(Allocation.primary_15) + fn.SUM(Allocation.primary_20) + fn.sum(Allocation.secondary_5) + fn.SUM(Allocation.secondary_10)).where(Allocation.department == dept, Allocation.termCode == 202500).scalar()
#     usedAllocation = len([hours for hours in LaborStatusForm.select(LaborStatusForm.weeklyHours).where(LaborStatusForm.department == dept, LaborStatusForm.termCode == 202500, LaborStatusForm.contractHours.is_null(True))])
#     studentHours = {}
#     for form in LaborStatusForm.select().where(LaborStatusForm.department == dept,LaborStatusForm.termCode_id == 202500,LaborStatusForm.contractHours.is_null(True)
#     ):
#         studentSuperviseeId = form.studentSupervisee_id
#         if studentSuperviseeId not in studentHours:
#             studentHours[studentSuperviseeId] = []
#         studentHours[studentSuperviseeId].append({
#                 "jobType": form.jobType,
#                 "weeklyHours": form.weeklyHours
#             })
        

#     def count_workers(job_type, hours_bucket):
#         return LaborStatusForm.select().where(LaborStatusForm.department == dept, LaborStatusForm.termCode == 202500, LaborStatusForm.jobType == job_type, LaborStatusForm.weeklyHours == hours_bucket, LaborStatusForm.contractHours.is_null(True)).count()
    
#     usedPositions = {
#     "used_10": count_workers("Primary", "10"),
#     "used_12": count_workers("Primary", "12"),
#     "used_15": count_workers("Primary", "15"),
#     "used_20": count_workers("Primary", "20"),
#     "used_5_sec": count_workers("Secondary", "5"),
#     "used_10_sec": count_workers("Secondary", "10"),
# }
#     break_allocation = LaborStatusForm.select(LaborStatusForm.contractHours).where(LaborStatusForm.department == dept, LaborStatusForm.termCode == 202500, LaborStatusForm.contractHours.is_null(False))
#     sumBreak = sum(form.contractHours or 0 for form in break_allocation)
    
    if dept:
        try:
            totalPositions = getTotalAllocations(202500, dept)["totalAllocations"]
            usedAllocation = getContractedAllocations(202500, dept)
            sumBreak = usedAllocation["break_hours"]
            studentHours = getContractedAllocations(202500, dept)
            usedPositions = usedAllocation
            usedAllocation = usedAllocation["used_total"]
        except Exception as e:
            totalPositions = {}
            usedAllocation = {}
            sumBreak = 0
            studentHours = {}
            usedPositions = {}
            usedAllocation = 0
    else: 
        totalPositions = {}
        usedAllocation = {}
        sumBreak = 0
        studentHours = {}
        usedPositions = {}
        usedAllocation = 0
    
    positions = list(PositionHistory.select().where(PositionHistory.department == dept, PositionHistory.status == "Active").order_by(PositionHistory.positionTitle.asc())) if dept else []
    positionsList = []
    posUrl = []
    if not positions:
        positionsList = ["No active positions in this department"]
    else:
        for i in positions:
            positionsList.append(i.positionTitle + ": " + "(WLS " + str(i.wls) + ")")
            posUrl.append(str(i.positionCode))
            
    return render_template('main/departmentPortal.html', 
                           departments = departments,
                           department = dept,
                           allocation = allocation,
                           total_allocation = totalPositions,
                           used_allocation = usedAllocation,
                           term = g.openTerm.termName,
                           studentHours = studentHours,
                           usedPositions = usedPositions,
                           break_hours = sumBreak,
                           positions = positionsList,
                           posUrl = posUrl,
                           supervisors = supervisors,
                           laborCoordinators=laborCoordinators,
                           currentUser=g.currentUser
                           )


@main_bp.route('/department/<org>/<account>/managepositions', methods=['GET'])
def managePositions(org, account):
    try:
        dept = Department.get(Department.ORG == org, Department.ACCOUNT == account)
    except DoesNotExist:
        return render_template('errors/404.html'), 404

    positions = Tracy().getPositionsFromDepartment(org, account)
    print(positions)
    return render_template('main/managepositions.html',
                           department = dept,
                           department_name = dept.DEPT_NAME,
                           positions = positions
                           )

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
    
@main_bp.route('/department/<org>/<account>', methods=['GET'])
def ViewAllocations(org, account):
      
    try:
        dept = Department.get(Department.ORG == org, Department.ACCOUNT == account)
    except DoesNotExist:
        return render_template('errors/404.html'), 404
