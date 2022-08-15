from app.controllers.admin_routes import admin
from app.login_manager import require_login
from flask import render_template, request, json, jsonify, redirect, url_for, send_file
from app.models.term import Term
from app.models.department import Department
from app.models.supervisor import Supervisor
from app.models.student import Student
from app.models.laborStatusForm import LaborStatusForm
from app.models.formHistory import FormHistory
from app.models.historyType import HistoryType
from app.models.status import Status
from app.models.user import User
from app.models.studentLaborEvaluation import StudentLaborEvaluation
from app.controllers.admin_routes.allPendingForms import checkAdjustment
import operator
from functools import reduce
from app.controllers.main_routes.download import CSVMaker
from peewee import JOIN, prefetch

# Global variable that will store the query result.
# It is made global to be used later in creating CSV file.
formSearchResults = None
sleJoin = False

@admin.route('/admin/formSearch', methods=['GET', 'POST'])
def formSearch():
    '''
    When the request is GET the function populates the General Search interface dropdown menus with their corresponding values.
    If the request is POST it also populates the datatable with data based on user input.
    '''
    currentUser = require_login()
    if not currentUser or not currentUser.isLaborAdmin:
        return render_template('errors/403.html'), 403

    terms = LaborStatusForm.select(LaborStatusForm.termCode).distinct().order_by(LaborStatusForm.termCode.desc())
    departments = Department.select().order_by(Department.DEPT_NAME.asc())
    supervisors = Supervisor.select().order_by(Supervisor.FIRST_NAME.asc())
    students = Student.select().order_by(Student.FIRST_NAME.asc())

    if request.method == 'POST':
        return getDatatableData(request)

    return render_template('admin/formSearch.html',
                            title = "Form Search",
                            terms = terms,
                            supervisors = supervisors,
                            students = students,
                            departments = departments,
                            )

def getDatatableData(request):
    '''
    This function runs a query based on selected options in the front-end and retrieves the appropriate forms.
    Then, it puts all the retrieved data in appropriate form to be send to the ajax call in the formSearch.js file.
    '''

    # 'draw', 'start', 'length', 'order[0][column]', 'order[0][dir]' are built-in parameters, i.e.,
    # they are implicitly passed as part of the AJAX request when using datatable server-side processing
    draw = int(request.form.get('draw', -1))
    rowNumber = int(request.form.get('start', -1))
    rowsPerPage = int(request.form.get('length', -1))
    sortColIndex = int(request.form.get("order[0][column]", -1))
    order = request.form.get('order[0][dir]')
    queryFilterData = request.form.get('data')
    queryFilterDict = json.loads(queryFilterData)
    # Dictionary to match column indices with column names in the DB
    # It is used for identifying the column that needs to be sorted
    colIndexColNameMap = {  0: Term.termCode,
                            1: Department.DEPT_NAME,
                            2: Supervisor.FIRST_NAME,
                            3: Student.FIRST_NAME,
                            4: LaborStatusForm.POSN_CODE,
                            5: LaborStatusForm.weeklyHours,
                            6: LaborStatusForm.startDate,
                            7: User.username,
                            8: FormHistory.status,
                            9: FormHistory.historyType,
                            10: StudentLaborEvaluation.ID}

    termCode = queryFilterDict.get('termCode', "")
    departmentId = queryFilterDict.get('departmentID', "")
    supervisorId = queryFilterDict.get('supervisorID', "")
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

    global sleJoin
    # WHERE clause conditions are dynamically generated using model fields and selectpicker values
    for field, value in fieldValueMap.items():
        if value != "" and value:
            # "is" is used to compare the two peewee objects as opposed to "==" operator.
            if field is FormHistory.historyType:
                for val in value:
                    clauses.append(field == val)
            elif field is FormHistory.status:
                for val in value:
                    clauses.append(field == val)
            elif field is StudentLaborEvaluation.ID:
                sleJoin = value[0]       # LSF exists but SLE does not (LOJ)
            else:
                clauses.append(field == value)

    # This expression creates SQL AND operator between the conditions added to 'clauses' list
    expression = reduce(operator.and_, clauses)

    global formSearchResults
    formSearchResults = (FormHistory.select()
                        .join(LaborStatusForm, on=(FormHistory.formID == LaborStatusForm.laborStatusFormID))
                        .join(Department, on=(LaborStatusForm.department == Department.departmentID))
                        .join(Supervisor, on=(LaborStatusForm.supervisor == Supervisor.ID))
                        .join(Student, on=(LaborStatusForm.studentSupervisee == Student.ID))
                        .join(Term, on=(LaborStatusForm.termCode == Term.termCode))
                        .join(User, on=(FormHistory.createdBy == User.userID))

                        .where(expression))

    if sleJoin:
        if sleJoin == "evalMidyearMissing" or sleJoin == "evalMidyearComplete":
            #grab all the midyear evaluationStatus
            evalResults = StudentLaborEvaluation.select(StudentLaborEvaluation.formHistoryID).where(StudentLaborEvaluation.formHistoryID.formID.termCode == termCode, StudentLaborEvaluation.is_midyear_evaluation == True, StudentLaborEvaluation.is_submitted == True)
        else:
            #grab all the final evaluationStatus
            evalResults = StudentLaborEvaluation.select(StudentLaborEvaluation.formHistoryID).where(StudentLaborEvaluation.formHistoryID.formID.termCode == termCode, StudentLaborEvaluation.is_midyear_evaluation == False, StudentLaborEvaluation.is_submitted == True)
        if sleJoin == "evalMidyearMissing":
            formSearchResults = formSearchResults.select().where(FormHistory.formHistoryID.not_in(evalResults))
        elif sleJoin == "evalMidyearComplete":
            formSearchResults = formSearchResults.select().where(FormHistory.formHistoryID.in_(evalResults))
        elif sleJoin == "evalMissing":
            formSearchResults = formSearchResults.select().where(FormHistory.formHistoryID.not_in(evalResults))
        elif sleJoin == "evalComplete":
            formSearchResults = formSearchResults.select().where(FormHistory.formHistoryID.in_(evalResults))

    recordsTotal = formSearchResults.count()

    # Sorting a column in descending order when a specific column is chosen
    # Initially, it sorts by the Term column as specified in formSearch.js
    if order == "desc":
        filteredSearchResults = formSearchResults.order_by(-colIndexColNameMap[sortColIndex]).limit(rowsPerPage).offset(rowNumber)
    # Sorting a column in ascending order when a specific column is chosen
    else:
        filteredSearchResults = formSearchResults.order_by(colIndexColNameMap[sortColIndex]).limit(rowsPerPage).offset(rowNumber)

    formattedData = getFormattedData(filteredSearchResults)
    formsDict = {"draw": draw, "recordsTotal": recordsTotal, "recordsFiltered": recordsTotal, "data": formattedData}

    return jsonify(formsDict)

def getFormattedData(filteredSearchResults):
    '''
    Putting the data in the correct format to be used by the JS file.
    Because this implementation is using server-side processing of datatables,
    the HTML for the datatables are also formatted here.
    '''

    supervisorStudentHTML = '<a href="#" class="hover_indicator" aria-label="{}">{} </a><a href="mailto:{}"><span class="glyphicon glyphicon-envelope mailtoIcon"></span></a>'
    departmentHTML = '<a href="#" class="hover_indicator" aria-label="{}-{}"> {}</a>'
    positionHTML = '<a href="#" class="hover_indicator" aria-label="{}"> {}</a>'
    formattedData = []
    for form in filteredSearchResults:
        # The order in which you append the items to 'record' matters and it should match the order of columns on the table!
        record = []
        # Term
        record.append(form.formID.termCode.termName)
        # Department
        record.append(departmentHTML.format(
              form.formID.department.ORG,
              form.formID.department.ACCOUNT,
              form.formID.department.DEPT_NAME))
        # Supervisor
        supervisorField = supervisorStudentHTML.format(
                            form.formID.supervisor.ID,
                            f'{form.formID.supervisor.FIRST_NAME} {form.formID.supervisor.LAST_NAME}',
                            form.formID.supervisor.EMAIL)
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
                newSupervisor = supervisorStudentHTML.format(
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

        record.append(supervisorField)
        # Student
        record.append(supervisorStudentHTML.format(
              form.formID.studentSupervisee.ID,
              f'{form.formID.studentSupervisee.FIRST_NAME} {form.formID.studentSupervisee.LAST_NAME}',
              form.formID.studentSupervisee.STU_EMAIL))

        record.append(f'{positionField}<br>{form.formID.jobType}')
        record.append(hoursField)
        # Contract Dates
        record.append("<br>".join([form.formID.startDate.strftime('%m/%d/%y'),
                                   form.formID.endDate.strftime('%m/%d/%y')]))
        # Created By
        record.append(supervisorStudentHTML.format(
              form.createdBy.supervisor.ID if form.createdBy.supervisor else form.createdBy.student.ID,
              form.createdBy.username,
              form.createdBy.email,
              form.createdDate.strftime('%m/%d/%y')))

        # Form Status
        record.append(form.status.statusName)
        # Form Type
        formTypeNameMapping = {
            "Labor Status Form": "Original",
            "Labor Adjustment Form": "Adjusted",
            "Labor Overload Form": "Overload",
            "Labor Release Form": "Release"}
        originalFormTypeName = form.historyType.historyTypeName
        mappedFormTypeName = formTypeNameMapping[originalFormTypeName]
        record.append(mappedFormTypeName)

        # Evaluation status
        # TODO Skipping adding to the table. Requires database work to get SLE out from form (formHistory, to be precise)

        laborHistoryId = form.formHistoryID
        laborStatusFormId = form.formID.laborStatusFormID
        actionsButton = getActionButtonLogic(form, laborHistoryId, laborStatusFormId)

        record.append(actionsButton)
        formattedData.append(record)

    return formattedData


def getActionButtonLogic(form, laborHistoryId, laborStatusFormId):
    '''
    This function determines the options shown on the Actions dropdown, which depends on form type and form status.
    '''

    actionsButtonDropdownHTML = '<div class="dropdown"><button class="btn btn-primary dropdown-toggle" type="button" id="menu1" data-toggle="dropdown">Actions <span class="caret"></span></button>' +\
                                '<ul class="dropdown-menu" role="menu" aria-labelledby="menu1" style="min-width: 100%;">{}{}{}{}{}</ul></div>'
    actionsListHTML = '<li role="presentation"><a role="menuitem" href="{}">{}</a></li>'
    manageOptionHTML = actionsListHTML.format('#', '<span id="{}" onclick="{}">{}</span>')
    denyApproveNotesOptionsHTML = actionsListHTML.format('#', '<span id="{}" onclick="{}" data-toggle="modal" data-target="#{}">{}</span>')
    modifyOptionHTML = actionsListHTML.format('/alterLSF/{lsfID}', '<span id="edit_{lsfID}">Modify</span>')

    # Actions button and its options
    actionsButton = ""
    approve = ""
    deny = ""
    manage = ""
    modify = ""
    notes = ""

    if form.historyType.historyTypeName == "Labor Status Form":
        manage = manageOptionHTML.format(laborHistoryId, f"loadLaborHistoryModal({laborStatusFormId})", 'Labor History')
        actionsButton = actionsButtonDropdownHTML.format(manage, approve, deny, modify, notes)

    if form.status.statusName in ("Pending", "Pre-Student Approval"):
        # show notes modal for all pending labor status forms
        notes = denyApproveNotesOptionsHTML.format(f'notes_{laborHistoryId}', f'getNotes({laborStatusFormId})', 'NotesModal', 'View Notes')
        if form.overloadForm:
            manage = manageOptionHTML.format(laborHistoryId, f"loadOverloadModal({laborHistoryId}, {laborStatusFormId})", 'Manage')
        elif form.releaseForm:
            manage = manageOptionHTML.format(laborHistoryId, f"loadReleaseModal({laborHistoryId}, {laborStatusFormId})", 'Manage')
        elif form.adjustedForm:
            deny = denyApproveNotesOptionsHTML.format(f"reject_{laborHistoryId}", f"insertDenial({laborHistoryId})", 'denyModal', 'Deny')
            approve = denyApproveNotesOptionsHTML.format("", f"insertApprovals({laborHistoryId})", 'approvalModal', 'Approve')
        else: # if it is the original labor status form
            modify = modifyOptionHTML.format(lsfID = laborStatusFormId)
            deny = denyApproveNotesOptionsHTML.format(f"reject_{laborHistoryId}", f"insertDenial({laborHistoryId})", 'denyModal', 'Deny')
            approve = denyApproveNotesOptionsHTML.format("", f"insertApprovals({laborHistoryId});", 'approvalModal', 'Approve')
        actionsButton = actionsButtonDropdownHTML.format(manage, approve, deny, modify, notes)

    return actionsButton


@admin.route('/admin/formSearch/download', methods=['POST'])
def downloadFormSearchResults():
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
    excel = CSVMaker("formSearch", formSearchResults, includeEvals = includeEvals)
    return send_file(excel.relativePath, as_attachment=True, attachment_filename=excel.relativePath.split('/').pop())
