import csv
import io
import json

from flask import g
from fpdf import FPDF
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

def makePositionDescriptionPDF(department, position):
    '''
    Builds a PDF of a position's description for the download button on the individual position page
    '''
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, department.DEPT_NAME, ln=True)
    pdf.ln(2)

    fields = [
        ('Position Title', position.positionTitle),
        ('Position Code', position.positionCode),
        ('WLS Level', position.wls),
        ('Status', position.status),
        ('Last Revision Date', position.revisionDate),
        ('Revised By', position.revisedBy or 'Unknown'),
    ]
    labelWidth = 45
    for label, value in fields:
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(labelWidth, 8, f'{label}:', ln=False)
        pdf.set_font('Arial', '', 11)
        pdf.cell(0, 8, f' {value}', ln=True)

    pdf.ln(4)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Description', ln=True)
    pdf.set_font('Arial', '', 11)
    description = position.description or 'No description available.'
    pdf.multi_cell(0, 7, description.encode('latin-1', 'replace').decode('latin-1'))

    pdfBytes = pdf.output(dest='S').encode('latin-1', 'replace')
    return io.BytesIO(pdfBytes)


class CSVMaker:
    '''
    Create the CSV for the download bottons
    '''
    def __init__(self, downloadName, requestedLSFs: ModelSelect, includeEvals = False, additionalSpreadsheetFields: list[str] = []):
        self.relativePath = f'static/files/{downloadName}.csv'
        self.completePath = 'app/' + self.relativePath
        self.additionalSpreadsheetFields = (self._validateAdditionalSpreadsheetFields(additionalSpreadsheetFields))
        self.formHistories = requestedLSFs 
        self.includeEvals = includeEvals
        self.makeCSV()
        
    @staticmethod
    def _validateAdditionalSpreadsheetFields(additionalFields):
        for additionalField in additionalFields:
            if additionalField not in {'overloads', 'finalEvaluations', 'midYearEvaluations', 'allEvaluations'}:
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
            if self.includeEvals:
                headers.extend(['SLE Type',
                                'SLE Attendance',
                                'SLE Attendance Comments',
                                'SLE Accountability',
                                'SLE Accountability Comments',
                                'SLE Teamwork',
                                'SLE Teamwork Comments',
                                'SLE Initiative',
                                'SLE Initiative Comments',
                                'SLE Respect',
                                'SLE Respect Comments',
                                'SLE Learning',
                                'SLE Learning Comments',
                                'SLE Job Specific',
                                'SLE Job Specific Comments',
                                'SLE Overall Score'
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
                if self.includeEvals:
                    evalRows = self.addEvaluationData(form.formHistoryID)
                    if len(evalRows) == 0:
                        self.filewriter.writerow(row)
                    elif len(evalRows) == 1:
                        row.extend(evalRows[0])
                        self.filewriter.writerow(row)
                    else:
                        row.extend(evalRows[0])
                        self.filewriter.writerow(row)
                        for evaluation in evalRows[1:]:
                            row = [""] * 17
                            row.extend(evaluation)
                            self.filewriter.writerow(row)

                elif 'overloads' in self.additionalSpreadsheetFields:
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


    def addEvaluationData(self, formID):
        '''
        Adds data for SLE
        '''
        multipleRows = []
        if "finalEvaluations" in self.additionalSpreadsheetFields:
            finalEvaluation = StudentLaborEvaluation.get_or_none(StudentLaborEvaluation.formHistoryID == formID, StudentLaborEvaluation.is_midyear_evaluation == 0, StudentLaborEvaluation.is_submitted == True)
            if finalEvaluation:
                multipleRows.append(self.insertEvaluationData(finalEvaluation, "Final"))
        elif "midYearEvaluations" in self.additionalSpreadsheetFields:
            midyearEvaluation = StudentLaborEvaluation.get_or_none(StudentLaborEvaluation.formHistoryID == formID, StudentLaborEvaluation.is_midyear_evaluation == 1, StudentLaborEvaluation.is_submitted == True)
            if midyearEvaluation:
                multipleRows.append(self.insertEvaluationData(midyearEvaluation, "Midyear"))
        elif self.includeEvals == True:
            anyEvaluation = StudentLaborEvaluation.select().where(StudentLaborEvaluation.formHistoryID == formID, StudentLaborEvaluation.is_submitted == True)
            if anyEvaluation:
                for evaluation in anyEvaluation:
                    multipleRows.append(self.insertEvaluationData(evaluation, "Midyear" if evaluation.is_midyear_evaluation else "Final"))
        else:
            return []

        return multipleRows

    def insertEvaluationData(self, evaluation, evalType):
        '''
        Helper function for self.addEvaluationData(); Adds individual row's SLE data
        '''
        tableRow = []
        tableRow.extend([   evalType,
                            evaluation.attendance_score,
                            evaluation.attendance_comment,
                            evaluation.accountability_score,
                            evaluation.accountability_comment,
                            evaluation.teamwork_score,
                            evaluation.teamwork_comment,
                            evaluation.initiative_score,
                            evaluation.initiative_comment,
                            evaluation.respect_score,
                            evaluation.respect_comment,
                            evaluation.learning_score,
                            evaluation.learning_comment,
                            evaluation.jobSpecific_score,
                            evaluation.jobSpecific_comment
                        ])
        tableRow.append(evaluation.attendance_score +
                        evaluation.accountability_score +
                        evaluation.teamwork_score +
                        evaluation.initiative_score +
                        evaluation.respect_score +
                        evaluation.learning_score +
                        evaluation.jobSpecific_score
                       )
        return tableRow
