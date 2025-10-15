import operator
from datetime import datetime, date
from functools import reduce

from flask import json, jsonify, g, make_response
from peewee import fn, Case

from app.controllers.admin_routes.allPendingForms import checkAdjustment
from app.logic.search import getDepartmentsForSupervisor
from app.logic.download import saveFormSearchResult
from app.models.term import Term
from app.models.department import Department
from app.models.supervisor import Supervisor
from app.models.student import Student
from app.models.laborStatusForm import LaborStatusForm
from app.models.formHistory import FormHistory
from app.models.user import User
from app.models.studentLaborEvaluation import StudentLaborEvaluation

def getDatatableData(request):
    '''
    This function runs a query based on selected options in the front-end and retrieves the appropriate forms.
    Then, it puts all the retrieved data in appropriate form to be send to the ajax call in the supervisorPortal.js file.
    '''
    # 'draw', 'start', 'length', 'order[0][column]', 'order[0][dir]' are built-in parameters, i.e.,
    # they are implicitly passed as part of the AJAX request when using datatable server-side processing
    
    sleJoin = ""
    draw = int(request.form.get('draw', 0))
    rowNumber = int(request.form.get('start', 0))
    rowsPerPage = int(request.form.get('length', 25))
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
                sleJoin=value[0]
            else:
                clauses.append(field == value)
    # This expression creates SQL AND operator between the conditions added to 'clauses' list
    formSearchResults = (FormHistory.select()
                                    .join(LaborStatusForm, on=(FormHistory.formID == LaborStatusForm.laborStatusFormID))
                                    .join(Department, on=(LaborStatusForm.department == Department.departmentID))
                                    .join(Supervisor, on=(LaborStatusForm.supervisor == Supervisor.ID))
                                    .join(Student, on=(LaborStatusForm.studentSupervisee == Student.ID))
                                    .join(Term, on=(LaborStatusForm.termCode == Term.termCode))
                                    .join(User, on=(FormHistory.createdBy == User.userID)))
    if clauses:
        formSearchResults = formSearchResults.where(reduce(operator.and_, clauses))
    if not g.currentUser.isLaborAdmin:
        supervisorDepartments = [d.departmentID for d in getDepartmentsForSupervisor(g.currentUser)]
        formSearchResults = formSearchResults.where(FormHistory.formID.department.in_(supervisorDepartments)) 
    recordsTotal = len(formSearchResults)

    # this checks and finds the first value that is not null of preferred_name, legal_name and last_name.
    # including last_name is necessary because there are like 4 cases where someone has no first name or last name, instead their full name is
    # stored in last_name
    supervisorFirstNameCase = fn.COALESCE(fn.NULLIF(Supervisor.preferred_name, ''), fn.NULLIF(Supervisor.legal_name, ''), Supervisor.LAST_NAME)
    studentFirstNameCase = fn.COALESCE(fn.NULLIF(Student.preferred_name, ''), fn.NULLIF(Student.legal_name, ''), Student.LAST_NAME)

    # this maps all of the values we expect to receive from the sorting dropdowns in the frontend 
    # to actual peewee objects we can sort by later
    # the casing is weird because the columns that don't have any fields are are not capitalized
    sortValueColumnMap = {
        "term": Term.termCode,
        "department": Department.DEPT_NAME,
        "supervisorFirstName": supervisorFirstNameCase,
        "supervisorLastName": Supervisor.LAST_NAME,
        "studentFirstName": studentFirstNameCase,
        "studentLastName": Student.LAST_NAME,
        "positionWLS": LaborStatusForm.WLS,
        "positionTitle": LaborStatusForm.POSN_TITLE,
        "positionType": LaborStatusForm.jobType,
        "length": LaborStatusForm.startDate,
        "createdBy": User.username, 
        "formStatus": FormHistory.status,
        "formType": FormHistory.historyType,
    }

    if order == "DESC":
        filteredSearchResults = formSearchResults.order_by(fn.TRIM(sortValueColumnMap[sortBy]).desc()).limit(rowsPerPage).offset(rowNumber)
    else:
        filteredSearchResults = formSearchResults.order_by(fn.TRIM(sortValueColumnMap[sortBy]).asc()).limit(rowsPerPage).offset(rowNumber)
    formattedData = getFormattedData(filteredSearchResults, queryFilterDict.get('view'))

    downloadId = saveFormSearchResult("Form Search", formSearchResults, "LSF Search")
    formsDict = {"draw": draw, "recordsTotal": recordsTotal, "recordsFiltered": recordsTotal, "data": formattedData, "downloadId": downloadId}

    return make_response(jsonify(formsDict))

def getFormattedData(filteredSearchResults, view ='simple'):
    '''
    Putting the data in the correct format to be used by the JS file.
    Because this implementation is using server-side processing of datatables,
    the HTML for the datatables are also formatted here.
    '''
    if view == "simple":
        formattedData = {}
        todaysDate = date.today()
        filteredSearchResults.order_by(FormHistory.formID.startDate.desc())
        isMostCurrent = False
        for form in filteredSearchResults:
            startDate = form.formID.startDate
            endDate = form.formID.endDate
            bNumber = form.formID.studentSupervisee.ID
            if bNumber not in formattedData:
                absentInFormatting = True
            else:
                absentInFormatting = False 
                isMostCurrent = (startDate > formattedData[bNumber][1]) or (startDate <= todaysDate <= endDate)
            if absentInFormatting or isMostCurrent:
                
                # html fields
                firstName, lastName = form.formID.studentSupervisee.FIRST_NAME, form.formID.studentSupervisee.LAST_NAME
                term = form.formID.termCode.termName
                positionTitle = form.formID.POSN_TITLE
                jobType = form.formID.jobType
                departmentName = form.formID.department.DEPT_NAME
                statusFormId = form.formID.laborStatusFormID

                formStatus = str(form.status)
                displayStatus = formStatus
                if form.overloadForm is not None:
                    displayStatus = "Overload " + formStatus
                if form.releaseForm is not None:
                    displayStatus = "Release Pending" if formStatus == "Pending" else "Released"

                html = f"""
                <a href="/laborHistory/{bNumber}">
                    <span class="h4">{firstName} {lastName} ({bNumber})</span>
                </a>
                <span class="pushRight">{displayStatus}</span>
                <br>
                <span class="pushLeft h6">
                    {term} - <a><span onclick=loadFormHistoryModal({statusFormId})>{positionTitle} ({jobType})</span></a> - {departmentName}
                </span>
                """

                formattedData[bNumber] = (html, startDate, endDate)

        formattedDataList = [[value] for value, _, _ in formattedData.values()]

        return formattedDataList

    # now in advanced view

    supervisorHTML = '<span href="#" aria-label="{}">{} </span><a href="mailto:{}"><span class="glyphicon glyphicon-envelope mailtoIcon"></span></span>'
    studentHTML = '<div><a href="/laborHistory/{}">{}</a><br>{} <a href="mailto:{}"><span class="glyphicon glyphicon-envelope mailtoIcon"></span></span></a></div>'
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
                        form.formID.jobType,
                        f'{form.formID.jobType} ({form.formID.WLS})')
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

        record.append(f'<a><span onclick=loadFormHistoryModal({form.formID.laborStatusFormID})>{form.formID.POSN_TITLE}</span></a><br>{positionField}')
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

        formattedData.append(record)

    return formattedData
