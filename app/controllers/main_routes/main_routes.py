import sys
import operator
from flask import render_template, request, json, jsonify, redirect, url_for, send_file, flash, g
from functools import reduce
from peewee import fn, Case
from datetime import datetime
from app.models.term import Term
from app.models.department import Department
from app.models.supervisor import Supervisor
from app.models.supervisorDepartment import SupervisorDepartment
from app.models.student import Student
from app.models.laborStatusForm import LaborStatusForm
from app.models.formHistory import FormHistory
from app.models.historyType import HistoryType
from app.models.status import Status
from app.models.user import User
from app.models.studentLaborEvaluation import StudentLaborEvaluation
from app.controllers.admin_routes.allPendingForms import checkAdjustment
from app.controllers.main_routes import main_bp
from app.controllers.main_routes.download import CSVMaker
from app.logic.search import getDepartmentsForSupervisor
from app.login_manager import require_login, logout


@main_bp.before_app_request
def before_request():
    pass # TODO Do we need to do anything here? User stuff?

@main_bp.route('/logout', methods=['GET'])
def logout():
    return redirect(logout())

# Global variable that will store the query result.
# It is made global to be used later in creating CSV file.
formSearchResults = None
sleJoin = False

@main_bp.route('/', methods=['GET', 'POST'])
def supervisorPortal():
    '''
    When the request is GET the function populates the General Search interface dropdown menus with their corresponding values.
    If the request is POST it also populates the datatable with data based on user input.
    '''
    currentUser = require_login()
    if not currentUser or not currentUser.supervisor:
        return render_template('errors/403.html'), 403
    
    terms = LaborStatusForm.select(LaborStatusForm.termCode).distinct().order_by(LaborStatusForm.termCode.desc())
    allSupervisors = Supervisor.select()
    supervisorFirstName = fn.COALESCE(Supervisor.preferred_name, Supervisor.legal_name)
    studentFirstName = fn.COALESCE(Student.preferred_name, Student.legal_name)

    if currentUser.isLaborAdmin or currentUser.isFinancialAidAdmin or currentUser.isSaasAdmin:
        departments = Department.select().order_by(Department.isActive.desc(), Department.DEPT_NAME.asc())
        departments = [department for department in departments]
        supervisors = (Supervisor.select(Supervisor, supervisorFirstName)
                                 .order_by(Supervisor.isActive.desc(), supervisorFirstName.contains("Unknown"), supervisorFirstName, Supervisor.LAST_NAME))
        students = (Student.select(Student, studentFirstName)
                           .order_by(studentFirstName.contains("Unknown"), studentFirstName, Student.LAST_NAME))

    else:
        departments = getDepartmentsForSupervisor(currentUser).order_by(Department.isActive.desc(), Department.DEPT_NAME.asc())
        departments = [department for department in departments] 
        deptNames = [department.DEPT_NAME for department in departments]

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
                            department = None,
                            currentUser = currentUser
                            )

def getDatatableData(request):
    '''
    This function runs a query based on selected options in the front-end and retrieves the appropriate forms.
    Then, it puts all the retrieved data in appropriate form to be send to the ajax call in the supervisorPortal.js file.
    '''
    # 'draw', 'start', 'length', 'order[0][column]', 'order[0][dir]' are built-in parameters, i.e.,
    # they are implicitly passed as part of the AJAX request when using datatable server-side processing
    global sleJoin
    if sleJoin:
        sleJoin = False
    
    currentUser = require_login()
    draw = int(request.form.get('draw', -1))
    rowNumber = int(request.form.get('start', -1))
    rowsPerPage = int(request.form.get('length', -1))
    queryFilterData = request.form.get('data')
    queryFilterDict = json.loads(queryFilterData)
    sortBy = queryFilterDict.get('sortBy', "term")
    if sortBy == "":
        sortBy = "term"
    order = queryFilterDict.get('order', "ASC")
    
    termCode = queryFilterDict.get('termCode', "")
    if termCode == "currentTerm":
        termCode = g.openTerm
    elif termCode == "activeTerms":
        termCode = list(Term.select(Term.termCode).where(Term.termEnd >= datetime.now()))
    departmentId = queryFilterDict.get('departmentID', "")
    supervisorId = queryFilterDict.get('supervisorID', "")
    if supervisorId == "currentUser":
        supervisorId = g.currentUser.supervisor
    studentId = queryFilterDict.get('studentID', "")
    formStatusList = queryFilterDict.get('formStatus', "") # form status radios
    formTypeList = queryFilterDict.get('formType', "") # form type radios
    evaluationStatus = queryFilterDict.get('evaluations', "") # evaluation radios

    fieldValueMap = {Term.termCode: termCode,
                     Department.departmentID: departmentId,
                     Student.ID: studentId,
                     Supervisor.ID: supervisorId,
                     FormHistory.status: formStatusList,
                     FormHistory.historyType: formTypeList,
                     StudentLaborEvaluation.ID: evaluationStatus}
    clauses = []
    # WHERE clause conditions are dynamically generated using model fields and selectpicker values
    for field, value in fieldValueMap.items():
        if value != "" and value:
            if type(value) is list:
                clauses.append(field.in_(value))
            elif field is StudentLaborEvaluation.ID:
                sleJoin = value[0]       
            else:
                clauses.append(field == value)
    # This expression creates SQL AND operator between the conditions added to 'clauses' list
    global formSearchResults
    formSearchResults = (FormHistory.select()
                                    .join(LaborStatusForm, on=(FormHistory.formID == LaborStatusForm.laborStatusFormID))
                                    .join(Department, on=(LaborStatusForm.department == Department.departmentID))
                                    .join(Supervisor, on=(LaborStatusForm.supervisor == Supervisor.ID))
                                    .join(Student, on=(LaborStatusForm.studentSupervisee == Student.ID))
                                    .join(Term, on=(LaborStatusForm.termCode == Term.termCode))
                                    .join(User, on=(FormHistory.createdBy == User.userID)))
    if clauses:
        formSearchResults = formSearchResults.where(reduce(operator.and_, clauses))
    if not currentUser.isLaborAdmin:
        supervisorDepartments = getDepartmentsForSupervisor(currentUser)
        formSearchResults = formSearchResults.where(FormHistory.formID.department.in_(supervisorDepartments)) 

    recordsTotal = len(formSearchResults)
    

    # this checks and finds the first value that is not null of preferred_name, legal_name and last_name.
    # including last_name is necessary because there are like 4 cases where someone has no first name or last name, instead their full name is
    # stored in last_name
    supervisorFirstNameCase = fn.COALESCE(fn.NULLIF(Supervisor.preferred_name, ''), fn.NULLIF(Supervisor.legal_name, ''), Supervisor.LAST_NAME)
    studentFirstNameCase = fn.COALESCE(fn.NULLIF(Student.preferred_name, ''), fn.NULLIF(Student.legal_name, ''), Student.LAST_NAME)

    # this maps all of the values we expect to receive from the sorting dropdowns in the frontend 
    # to actual peewee objects we can sort by later
    sortValueColumnMap = {
        "term": Term.termCode,
        "department": Department.DEPT_NAME,
        "supervisorFirstName": supervisorFirstNameCase,
        "supervisorLastName": Supervisor.LAST_NAME,
        "studentFirstName": studentFirstNameCase,
        "studentLastName": Student.LAST_NAME,
        "positionType": LaborStatusForm.POSN_TITLE,
        "positionCode": LaborStatusForm.POSN_CODE,
        "positionWLS": LaborStatusForm.WLS,
        "hours": LaborStatusForm.weeklyHours,
        "length": LaborStatusForm.startDate,
        "createdBy": User.username, 
        "formStatus": FormHistory.status,
        "formType": FormHistory.historyType,
    }

    if order == "DESC":
        filteredSearchRcesults = formSearchResults.order_by(sortValueColumnMap[sortBy].desc()).limit(rowsPerPage).offset(rowNumber)
    else:
        filteredSearchResults = formSearchResults.order_by(sortValueColumnMap[sortBy].asc()).limit(rowsPerPage).offset(rowNumber)
    formattedData = getFormattedData(filteredSearchResults)
    formsDict = {"draw": draw, "recordsTotal": recordsTotal, "recordsFiltered": recordsTotal, "data": formattedData}

    return jsonify(formsDict)

def getFormattedData(filteredSearchResults):
    '''
    Putting the data in the correct format to be used by the JS file.
    Because this implementation is using server-side processing of datatables,
    the HTML for the datatables are also formatted here.
    '''

    supervisorHTML = '<span href="#" aria-label="{}">{} </span><a href="mailto:{}"><span class="glyphicon glyphicon-envelope mailtoIcon"></span></span>'
    studentHTML = '<div><a><span onclick=loadLaborHistoryModal({}) aria-label="{}">{} </span></a><br>{} <a href="mailto:{}"><span class="glyphicon glyphicon-envelope mailtoIcon"></span></span></a></div>'
    departmentHTML = '<span href="#" aria-label="{}-{}"> {}</span>'
    positionHTML = '<span href="#" aria-label="{}"> {}</span>'
    formTypeStatus = '<span href="#" aria-label=""> {}</span>'
    formattedData = []
    for form in filteredSearchResults:
        # The order in which you append the items to 'record' matters and it should match the order of columns on the table!
        record = []
        # Term
        record.append(form.formID.termCode.termName)
        # Student
        record.append(studentHTML.format(
                form.formID.laborStatusFormID,
              form.formID.studentSupervisee.ID,
              f'{form.formID.studentSupervisee.preferred_name if form.formID.studentSupervisee.preferred_name else form.formID.studentSupervisee.legal_name} {form.formID.studentSupervisee.LAST_NAME}',
              form.formID.studentSupervisee.ID,
              form.formID.studentSupervisee.STU_EMAIL))
        # Supervisor
        supervisorField = supervisorHTML.format(
                            form.formID.supervisor.ID,
                            f'{form.formID.supervisor.preferred_name if form.formID.supervisor.preferred_name else form.formID.supervisor.legal_name } {form.formID.supervisor.LAST_NAME}',
                            form.formID.supervisor.EMAIL)
        record.append(supervisorField)
        
        # Department
        record.append(departmentHTML.format(
              form.formID.department.ORG,
              form.formID.department.ACCOUNT,
              form.formID.department.DEPT_NAME))
        
        # Position
        positionField = positionHTML.format(
                        form.formID.POSN_TITLE,
                        f'{form.formID.POSN_CODE} ({form.formID.WLS})')
        # Hours
        hoursField = form.formID.weeklyHours if form.formID.weeklyHours else form.formID.contractHours
        # Adjustment Form Specific Data
        checkAdjustment(form)
        if (form.adjustedForm):
            if form.adjustedForm.fieldAdjusted == "supervisor":
                newSupervisor = supervisorHTML.format(
                                form.adjustedForm.oldValue['ID'],
                                form.adjustedForm.newValue,
                                form.adjustedForm.oldValue['email'])
                supervisorField = f'<s aria-label="true">{supervisorField}</s><br>{newSupervisor}'

            if form.adjustedForm.fieldAdjusted == "position":
                newPosition = positionHTML.format(
                              form.adjustedForm.oldValue,
                              form.adjustedForm.newValue)
                positionField = f'<s aria-label="true">{positionField}</s><br>{newPosition}'

            if form.adjustedForm.fieldAdjusted == "weeklyHours"  or  form.adjustedForm.fieldAdjusted == "contractHours":
                newHours = form.adjustedForm.newValue
                hoursField = f'<s aria-label="true">{hoursField}</s><br>{newHours}'

        
        

        record.append(f'{form.formID.jobType}<br>{positionField}')
        record.append(hoursField)
        # Contract Dates
        record.append("<br>".join([form.formID.startDate.strftime('%m/%d/%y'),
                                   form.formID.endDate.strftime('%m/%d/%y')]))
        # Created By
        record.append(supervisorHTML.format(
              form.createdBy.supervisor.ID if form.createdBy.supervisor else form.createdBy.student.ID,
              form.createdBy.username,
              form.createdBy.email,
              form.createdDate.strftime('%m/%d/%y')))
        # Form Type
        formTypeNameMapping = {
            "Labor Status Form": "Original",
            "Labor Adjustment Form": "Adjusted",
            "Labor Overload Form": "Overload",
            "Labor Release Form": "Release"}
        originalFormTypeName = form.historyType.historyTypeName
        mappedFormTypeName = formTypeNameMapping[originalFormTypeName]
        # formType(Status)
        formTypeStatusField = record.append(formTypeStatus.format(f'{mappedFormTypeName} ({form.status.statusName})'))

        # Evaluation status
        # TODO: Skipping adding to the table. Requires database work to get SLE out from form (formHistory, to be precise)

        formattedData.append(record)

    return formattedData

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

    global formSearchResults
    global sleJoin
    if sleJoin == "evalComplete":
        includeEvals = "Final"
    elif sleJoin == "evalMidyearComplete":
        includeEvals = "Midyear"
    else:
        includeEvals = False

    formSearchResults = formSearchResults.order_by(-FormHistory.createdDate)
    excel = CSVMaker("supervisorPortal", formSearchResults, includeEvals = includeEvals)
    return send_file(excel.relativePath, as_attachment=True, attachment_filename=excel.relativePath.split('/').pop())
