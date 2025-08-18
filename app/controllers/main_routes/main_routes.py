from flask import render_template, request, json, redirect, url_for, send_file, g, flash
from peewee import fn
from app.models.department import Department
from app.models.supervisor import Supervisor
from app.models.supervisorDepartment import SupervisorDepartment
from app.models.student import Student
from app.models.laborStatusForm import LaborStatusForm
from app.models.formHistory import FormHistory
from app.controllers.admin_routes.allPendingForms import checkAdjustment
from app.controllers.main_routes import main_bp
from app.logic.download import CSVMaker, saveFormSearchResult, retrieveFormSearchResult
from app.logic.search import getDepartmentsForSupervisor
from app.login_manager import require_login, logout
from app.logic.getTableData import getDatatableData
from app.logic.banner import Banner

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
    
    terms = LaborStatusForm.select(LaborStatusForm.termCode).distinct().order_by(LaborStatusForm.termCode.desc())
    allSupervisors = Supervisor.select()
    supervisorFirstName = fn.COALESCE(Supervisor.preferred_name, Supervisor.legal_name)
    studentFirstName = fn.COALESCE(Student.preferred_name, Student.legal_name)
    department = None
    if currentUser.isLaborAdmin or currentUser.isFinancialAidAdmin or currentUser.isSaasAdmin:
        departments = list(Department.select().order_by(Department.isActive.desc(), Department.DEPT_NAME.asc()))
        supervisors = (Supervisor.select(Supervisor, supervisorFirstName)
                                 .order_by(Supervisor.isActive.desc(), supervisorFirstName.contains("Unknown"), supervisorFirstName, Supervisor.LAST_NAME))
        students = (Student.select(Student, studentFirstName)
                           .order_by(studentFirstName.contains("Unknown"), studentFirstName, Student.LAST_NAME))

    else:
        departments = list(getDepartmentsForSupervisor(currentUser).order_by(Department.isActive.desc(), Department.DEPT_NAME.asc()))
        deptNames = [department.DEPT_NAME for department in departments]

        supervisorPrimaryDepartment = Department.select().join(SupervisorDepartment) # count up all forms for a supervisor in department and get the max

        supervisors = (Supervisor.select(Supervisor, supervisorFirstName)
                                 .join_from(Supervisor, LaborStatusForm)
                                 .join_from(LaborStatusForm, Department)
                                 .where(Department.DEPT_NAME.in_(deptNames))
                                 .distinct()
                                 .order_by(Supervisor.isActive.desc(), supervisorFirstName.contains("Unknown"), supervisorFirstName, Supervisor.LAST_NAME))
        
        students = (Student.select(Student, studentFirstName)
                           .join_from(Student, LaborStatusForm)
                           .join_from(LaborStatusForm, Department)
                           .where(Department.DEPT_NAME.in_(deptNames))
                           .order_by(studentFirstName.contains("Unknown"), studentFirstName, Student.LAST_NAME)
                           .distinct())
    if request.method == 'POST':
        return getDatatableData(request)

    return render_template('main/supervisorPortal.html',
                            terms = terms,
                            supervisors = supervisors,
                            allSupervisors = allSupervisors,
                            students = students,
                            departments = departments,
                            department = department,
                            currentUser = currentUser
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

@main_bp.route('/lsf/<lsfId>/submitToBanner', methods=['GET'])
def submitToBanner(lsfId):
    if not (g.currentUser.isLaborAdmin or g.currentUser.isLaborDepartmentStudent):
        return render_template('errors/403.html'), 403      

    try:
        conn = Banner()
        save_form_status = conn.insert(lsfId)
    except Exception as e:
        save_form_status = False
        print(f"Error saving form history ({lsfId}) to Banner.")

    if save_form_status:
        return "Form successfully submitted to Banner.", 200
    else:
        return "Submitting to Banner failed.", 500


