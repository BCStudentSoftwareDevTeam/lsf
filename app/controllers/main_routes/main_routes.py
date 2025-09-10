from flask import render_template, request, json, redirect, url_for, send_file, g, flash, jsonify
from peewee import JOIN
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
    def searchSupervisorPortal(searchType, userInput):
        currentUser = require_login()
        if currentUser.isLaborAdmin or currentUser.isFinancialAidAdmin or currentUser.isSaasAdmin:
            allowed_departments = None  # unrestricted
        else:
            allowed_departments = [dept.DEPT_NAME for dept in getDepartmentsForSupervisor(currentUser)]

        if searchType == "termSelect":
            terms = Term.select().where(Term.termName.contains(userInput)).order_by(Term.termCode.desc())
            return [{'termCode': term.termCode, 'termName': term.termName} for term in terms]

        elif searchType == "departmentSelect":
            query = Department.select().where(Department.DEPT_NAME.contains(userInput))
            if allowed_departments is not None:
                query = query.where(Department.DEPT_NAME.in_(allowed_departments))
            query = query.order_by(Department.isActive.desc(), Department.DEPT_NAME.asc()).limit(10)
            return [
                {'DEPT_NAME': dept.DEPT_NAME, 'id': dept.departmentID, 'isActive': dept.isActive} 
                for dept in query
            ]

        elif searchType == "supervisorSelect":
            supervisor_query = search_person(Supervisor, userInput, allowed_departments)
            supervisor_query = supervisor_query.order_by(Supervisor.isActive.desc()).limit(10)
            return [
                {'id': sup.ID, 'FIRST_NAME': sup.FIRST_NAME, "LAST_NAME": sup.LAST_NAME, "isActive": sup.isActive} 
                for sup in supervisor_query
            ]

        elif searchType == "studentSelect":
            student_query = search_person(Student, userInput, allowed_departments)
            student_query = student_query.order_by(Student.LAST_NAME.asc()).limit(10)
            return [
                {'id': stu.ID, 'FIRST_NAME': stu.FIRST_NAME, 'LAST_NAME': stu.LAST_NAME} 
                for stu in student_query
            ]

        return []
    
    try:
        searchType = request.args.get("searchType")
        userInput = request.args.get("userInput")

        if not searchType or not userInput:
            return jsonify({""}), 400
        userList = searchSupervisorPortal(searchType, userInput)
        return jsonify(userList)
    except Exception as e:
        print('ERROR:', e, type(e))

def search_person(model, userInput, allowed_departments=None):
    """
    Returns a Peewee SelectObject filtered so that all words in userInput
    must appear in at least one of the model's fields.
    """
    words = userInput.strip().split()

    word_conditions = []
    for word in words:
        word_conditions.append(
            (model.preferred_name.contains(word)) |
            (model.legal_name.contains(word)) |
            (model.LAST_NAME.contains(word)) |
            (model.ID.contains(word))
        )

    query = model.select().where(reduce(operator.and_, word_conditions))

    if allowed_departments is not None:
        query = (
            query
            .join_from(model, LaborStatusForm, JOIN.LEFT_OUTER)
            .join_from(LaborStatusForm, Department, JOIN.LEFT_OUTER)
            .where(Department.DEPT_NAME.in_(allowed_departments))
            .distinct()
        )

    return query

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


