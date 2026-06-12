import csv
import json

from flask import g
from peewee import ModelSelect

from app.models.formHistory import *
from app.controllers.main_routes.main_routes import *
from app.models.studentLaborEvaluation import StudentLaborEvaluation
from app.models.formSearchResult import FormSearchResult

def saveFormSearchResult(displayName, formList, formType):
    ids = [form.formHistoryID for form in formList]

    result = FormSearchResult.create(name           = displayName,
                                     formHistoryIds = json.dumps(ids),
                                     searchType     = formType,
                                     generatedBy    = g.currentUser)

    return result.id

def retrieveFormSearchResult(formSearchResultId):
    result = FormSearchResult.get_by_id(formSearchResultId)

    # ensure we only give the result to the user who started the search
    if result.generatedBy == g.currentUser:
        return result

    return None

class CSVMaker:
    '''
    Create the CSV for the download bottons
    '''
    def __init__(self, downloadName, requestedLSFs: ModelSelect, additionalSpreadsheetFields: list[str] = []):
        self.relativePath = f'static/files/{downloadName}.csv'
        self.completePath = 'app/' + self.relativePath
        self.additionalSpreadsheetFields = (self._validateAdditionalSpreadsheetFields(additionalSpreadsheetFields))
        self.formHistories = requestedLSFs 
        self.makeCSV()
        
    @staticmethod
    def _validateAdditionalSpreadsheetFields(additionalFields):
        for additionalField in additionalFields:
            if additionalField not in {'overloads', 'allEvaluations'}:
                raise ValueError(f'Invalid spreadsheet fields: {additionalField}')
        return additionalFields

    def makeCSV(self):
        '''
        Creates the CSV file
        '''
        with open(self.completePath, 'w', encoding="utf-8", errors="backslashreplace") as csvfile:
            self.filewriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

            ## Create heading on csv ##
            headers =   ([  'Term',
                            'Form Type',
                            'Form Status',
                            'B#',
                            'Student Name',
                            'Student Email',
                            'Position',
                            'Labor Position Code',
                            'Labor Position Title',
                            'WLS',
                            'Weekly Hours',
                            'Total Contract Hours',
                            'Start Date',
                            'End Date',
                            'Department',
                            'Supervisor',
                            'Supervisor Email',
                            'Supervisor Notes'
                            ])
            
            if 'overloads' in self.additionalSpreadsheetFields:
                headers.extend(['Student Overload Reason',
                                'Financial Aid Status',
                                'Financial Aid Approver',
                                'Financial Aid Review Date',
                                'SAAS Status',
                                'SAAS Approver',
                                'SAAS Review Date',
                                'Labor Status',
                                'Labor Approver',
                                'Labor Review Date'])

            self.filewriter.writerow(headers)

            for form in self.formHistories:
                row = self.addPrimaryData(form)
                if 'overloads' in self.additionalSpreadsheetFields:
                    row = self.addOverloadData(form, row)
                    self.filewriter.writerow(row)
                else:
                    self.filewriter.writerow(row)


    def addPrimaryData(self, form):
        '''
        Adds data included on every CSV
        '''

        row = [ form.formID.termCode.termName,
                form.historyType_id,
                form.status_id,
                form.formID.studentSupervisee.ID,
                u' '.join((form.formID.studentSupervisee.FIRST_NAME, form.formID.studentSupervisee.LAST_NAME)),
                form.formID.studentSupervisee.STU_EMAIL,
                form.formID.jobType,
                form.formID.POSN_CODE,
                form.formID.POSN_TITLE,
                form.formID.WLS,
                form.formID.weeklyHours,
                form.formID.contractHours,
                form.formID.startDate,
                form.formID.endDate,
                form.formID.department.DEPT_NAME,
                u' '.join((form.formID.supervisor.FIRST_NAME, form.formID.supervisor.LAST_NAME)),
                form.formID.supervisor.EMAIL,
                form.formID.supervisorNotes
              ]
        return row

    def addOverloadData(self, form, rowData):

        faApprover = form.overloadForm.financialAidApprover.fullName if form.overloadForm.financialAidApprover else ""
        saasApprover = form.overloadForm.SAASApprover.fullName if form.overloadForm.SAASApprover else ""
        laborApprover = form.overloadForm.laborApprover.fullName if form.overloadForm.laborApprover else ""

        rowData.extend([
                form.overloadForm.studentOverloadReason, 
                form.overloadForm.financialAidApproved_id, 
                faApprover,
                form.overloadForm.financialAidReviewDate, 
                form.overloadForm.SAASApproved_id, 
                saasApprover,
                form.overloadForm.SAASReviewDate, 
                form.overloadForm.laborApproved_id, 
                laborApprover,
                form.overloadForm.laborReviewDate, 
            ])

        return rowData

    