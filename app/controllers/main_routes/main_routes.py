from flask import render_template, request, json, redirect, url_for, send_file, g, flash, jsonify
from peewee import fn, DoesNotExist
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
from app.models.user import User # remove later?
from app.logic.tracy import Tracy # remove later?

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
    
    terms = Term.select(Term.termName).order_by(Term.termCode.desc())
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

        supervisors = (Supervisor.select(Supervisor, supervisorFirstName)
                                 .join_from(Supervisor, LaborStatusForm)
                                 .join_from(LaborStatusForm, Department)
                                 .where(Department.DEPT_NAME.in_(departments))
                                 .distinct()
                                 .order_by(Supervisor.isActive.desc(), supervisorFirstName.contains("Unknown"), supervisorFirstName, Supervisor.LAST_NAME))
        
        students = (Student.select(Student, studentFirstName)
                           .join_from(Student, LaborStatusForm)
                           .join_from(LaborStatusForm, Department)
                           .where(Department.DEPT_NAME.in_(departments))
                           .order_by(studentFirstName.contains("Unknown"), studentFirstName, Student.LAST_NAME)
                           .distinct())
    if request.method == 'POST':
        return getDatatableData(request)

    return render_template('main/supervisorPortal.html',
                            terms = terms,
                            supervisors = supervisors,
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

# WORK IN PROGRESS---------------------------------------------------
@main_bp.route('/supervisorPortal/liveSearch', methods=['GET'])
def SupervisorPortalSearch():
    """
        ADD DESCRIPTION HERE
        Logic copied from adminManagement live search function
    """
    def searchSupervisorPortal(searchType, userInput):
        if searchType == "termSelect":
            termList = []
            terms = Term.select().where(Term.termName.contains(userInput)).order_by(Term.termCode.desc())
            for term in terms:
                termList.append({'termCode': term.termCode,
                                'termName': term.termName
                                })
            print("this is our term list:", termList)
            return termList
        elif searchType == "departmentSelect":
            pass
        elif searchType == "supervisorSelect":
            pass
        elif searchType == "studentSelect":
            pass

        # userList = []
        # if adminType == "addlaborAdmin":
        #     tracyStudents = Tracy().getStudentsFromUserInput(userInput)
        #     students = []
        #     for student in tracyStudents:
        #         try:
        #             existingUser = User.get(User.student == student.ID)
        #             if existingUser.isLaborAdmin:
        #                 pass
        #             else:
        #                 students.append(student)
        #         except DoesNotExist as e:
        #             students.append(student)
        #     for student in students:
        #         username = student.STU_EMAIL.split('@', 1)
        #         userList.append({'username': username[0],
        #                         'firstName': student.FIRST_NAME,
        #                         'lastName': student.LAST_NAME,
        #                         'type': 'Student'
        #                         })
        # tracySupervisors = Tracy().getSupervisorsFromUserInput(userInput)
        # supervisors = []
        # for supervisor in tracySupervisors:
        #     try:
        #         existingUser = User.get(User.supervisor == supervisor.ID)
        #         if ((existingUser.isLaborAdmin and adminType == "addlaborAdmin")
        #             or (existingUser.isSaasAdmin and adminType == "addSaasAdmin")
        #             or (existingUser.isFinancialAidAdmin and adminType == "addFinAidAdmin")):
        #             pass
        #         else:
        #             supervisors.append(supervisor)
        #     except DoesNotExist as e:
        #         supervisors.append(supervisor)
        # for sup in supervisors:
        #     username = sup.EMAIL.split('@', 1)
        #     userList.append({'username': username[0],
        #                     'firstName': sup.FIRST_NAME,
        #                     'lastName': sup.LAST_NAME,
        #                     'type': 'Supervisor'})
        # return userList
    
    # The acutal function code starts here***********************
    try:
        searchType = request.args.get("searchType")
        userInput = request.args.get("userInput")

        if not searchType or not userInput:
            return jsonify({""}), 400
        userList = searchSupervisorPortal(searchType, userInput)
        
        return jsonify(userList)
    except Exception as e:
        print('ERROR:', e, type(e))

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


