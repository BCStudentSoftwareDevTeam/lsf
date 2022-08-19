from flask import flash
from app.models.laborStatusForm import LaborStatusForm
from app.models.formHistory import *
import csv
from app.controllers.main_routes.main_routes import *
from app.models.supervisor import Supervisor
from app.logic.tracy import Tracy
from app.models.formHistory import FormHistory
from app.models.studentLaborEvaluation import StudentLaborEvaluation


class CSVMaker:
    '''
    Create the CSV for the download bottons
    '''
    def __init__(self, downloadType, requestedLSFs, includeEvals = False):
        self.relativePath = 'static/files/LaborStudents.csv'
        self.completePath = 'app/' + self.relativePath
        self.downloadType = downloadType          #studentHistory, allPending, studentList
        self.formHistories = self.retrieveFormHistories(requestedLSFs)
        self.includeEvals = includeEvals

        self.makeCSV()


    def retrieveFormHistories(self, requestedLSFs):
        '''
        Removes any duplicate formHistory IDs
        '''

        allForms = list(set(requestedLSFs)) # remove duplicates

        for statusForm in allForms:
            studentFormHistories = []
            if self.downloadType == "studentHistory":
                studentFormHistories = FormHistory.select().where(FormHistory.formID == statusForm)
            elif self.downloadType == "studentList":
                studentFormHistories = FormHistory.select().where(FormHistory.formID == statusForm, FormHistory.historyType == 'Labor Status Form')

            for historyForm in studentFormHistories:
                allForms.append(historyForm)

        return allForms


    def makeCSV(self):
        '''
        Creates the CSV file
        '''
        with open(self.completePath, 'w', encoding="utf-8", errors="backslashreplace") as csvfile:
            self.filewriter = csv.writer(csvfile, delimiter=',',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)

            ## Create heading on csv ##
            headers =   ([  'Term',
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
            
            if self.downloadType == 'includeOverloads':
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

                elif self.downloadType == "includeOverloads":
                    row = self.addOverloadData(form, row)
                    self.filewriter.writerow(row)
                else:
                    self.filewriter.writerow(row)


    def addPrimaryData(self, form):
        '''
        Adds data included on every CSV
        '''

        row = [ form.formID.termCode.termName,
                form.status.statusName,
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
        if self.includeEvals == "Final":
            finalEvaluation = StudentLaborEvaluation.get_or_none(StudentLaborEvaluation.formHistoryID == formID, StudentLaborEvaluation.is_midyear_evaluation == 0, StudentLaborEvaluation.is_submitted == True)
            if finalEvaluation:
                multipleRows.append(self.insertEvaluationData(finalEvaluation, "Final"))
        elif self.includeEvals == "Midyear":
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
