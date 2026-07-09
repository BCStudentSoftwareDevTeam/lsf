from flask import render_template, request, json, redirect, url_for, send_file, g, flash, jsonify
from flask_bootstrap import forms
from peewee import JOIN, DoesNotExist
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
    
    pos = Tracy().getPositionsFromDepartment(org, account)
    positions = []
    if pos == []:
        positions = ["No Positions for this Department"]
    else:
        for i in pos:
            positions.append(i.POSN_TITLE + "" + "(" + i.WLS + ")")

    staff = Tracy().getSupervisors()
    supervisors = []
    print(dept, '*********************************************************Denys')
    try:
        allocation = Allocation.select(Allocation, Term).join(Term).where(Allocation.department == dept, Allocation.termCode == 202500).get()
        print(allocation,g.openTerm.termCode,  '*********************************************************Scott')
    except DoesNotExist:
        allocation = None
    term = 202500
    ViewAllocations(org, account)
    for i in staff:
        if i.ORG == org:
            supervisors.append(i.FIRST_NAME + " " + i.LAST_NAME + " (" + i.EMAIL + ")")
    totalPositions = Allocation.select(Allocation.primary_10 + Allocation.primary_12 + Allocation.primary_15 + Allocation.primary_20 + Allocation.secondary_5 + Allocation.secondary_10).where(Allocation.department == dept, Allocation.termCode == 202500).scalar()
    usedAllocation = [hours for hours in LaborStatusForm.select(LaborStatusForm.weeklyHours).where(LaborStatusForm.department == dept, LaborStatusForm.termCode == 202500, LaborStatusForm.studentConfirmation.is_null(True))]
    usedAllocation = len(usedAllocation)
    student_hours = {}
    for form in LaborStatusForm.select().where(
        LaborStatusForm.department == dept,
        LaborStatusForm.termCode_id == 202500
    ):
        sid = form.studentSupervisee_id
        student_hours.setdefault(sid, []).append({
            "jobType": form.jobType,
            "weeklyHours": form.weeklyHours
        })
    for sid, jobs in student_hours.items():
        primary = sum(j["weeklyHours"] for j in jobs if j["jobType"] == "Primary")
        secondary = sum(j["weeklyHours"] for j in jobs if j["jobType"] == "Secondary")
        print(sid, "Primary:", primary, "Secondary:", secondary)
    def count_workers(job_type, hours_bucket):
        return LaborStatusForm.select().where(
            LaborStatusForm.department == dept,
            LaborStatusForm.termCode == 202500,
            LaborStatusForm.jobType == job_type,
            LaborStatusForm.weeklyHours == hours_bucket,
            LaborStatusForm.studentConfirmation.is_null(True)  # pending counts as "used" for now
        ).count()
    
    used_10     = count_workers("Primary", "10")
    used_12     = count_workers("Primary", "12")
    used_15     = count_workers("Primary", "15")
    used_20     = count_workers("Primary", "20")
    used_5_sec  = count_workers("Secondary", "5")
    used_10_sec = count_workers("Secondary", "10")
    print(usedAllocation, '*********************************************************hours_list')
    print(totalPositions, usedAllocation,Allocation.primary_10,  '*********************************************************brian')
    print(list(LaborStatusForm.select(LaborStatusForm.studentConfirmation).where(
    LaborStatusForm.department == dept,
    LaborStatusForm.termCode == 202500
)))
    return render_template('main/departmentPortal.html', 
                           departments = departments,
                           department = dept,
                           positions = positions,
                           supervisors = supervisors,
                           allocation = allocation,
                           total_allocation = totalPositions,
                           used_allocation = usedAllocation,
                           term = term,
                           studentHours = student_hours,
                           used_10 = used_10,
                           used_12 = used_12,
                           used_15 = used_15,
                           used_20 = used_20,
                           used_5_sec = used_5_sec,
                           used_10_sec = used_10_sec
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
    
@main_bp.route('/department/<org>/<account>', methods=['GET'])
def ViewAllocations(org, account):
      
    try:
        dept = Department.get(Department.ORG == org, Department.ACCOUNT == account)
    except DoesNotExist:
        return render_template('errors/404.html'), 404

    
    allocation = Allocation.select(Allocation, Term).join(Term).where(Allocation.department == dept, Allocation.termCode == g.openTerm)
    print(g.openTerm, '*********************************************************')
    term = g.openTerm.termName
    print(term, type(term), '*********************************************************')
    return render_template('main/departmentPortal.html',
                           department = dept,
                           department_name = dept.DEPT_NAME,
                           allocation = allocation,
                           term = term
                           )

