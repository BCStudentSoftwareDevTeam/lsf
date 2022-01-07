from flask import flash
from app.models.laborStatusForm import LaborStatusForm
from app.models.formHistory import *
import csv
from app.controllers.main_routes.main_routes import *
from app.models.supervisor import Supervisor
from app.logic.tracy import Tracy
from app.models.formHistory import FormHistory
from app.models.studentLaborEvaluation import StudentLaborEvaluation
class ExcelMaker:
    '''
    Create the excel for the download bottons
    '''
    def __init__(self):
        self.relativePath = 'static/files/LaborStudents5.csv'
        self.completePath = 'app/' + self.relativePath


    def makeExcelStudentHistory(self, formid):
        '''
        Creates a CSV of an individual students labor history
        '''
        downloadForms = []
        for id in formid:
            studentForms = FormHistory.select().where(FormHistory.formID == id) #, FormHistory.historyType == 'Labor Status Form'
            for studentForm in studentForms:
                downloadForms.append(studentForm)

        with open(self.completePath, 'w') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=',',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)

        ## Create heading on csv ##
            filewriter.writerow([   'Form type',
                                    'Student Name',
                                    'Student Email',
                                    'B#',
                                    'Term',
                                    'Department',
                                    'Supervisor',
                                    'Supervisor Email',
                                    'Position',
                                    'Labor Position Title',
                                    'Labor Position Code',
                                    'WLS',
                                    'Weekly Hours',
                                    'Total Contract Hours',
                                    'Start Date',
                                    'End Date',
                                    'Form Status',
                                    'Supervisor Notes',
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
                                    'SLE Overall Score',

                                ])
        ## fill infomations ##
            for form in downloadForms:
                row = [             form.historyType,
                                    form.formID.studentSupervisee.FIRST_NAME + " " + form.formID.studentSupervisee.LAST_NAME,
                                    form.formID.studentSupervisee.STU_EMAIL,
                                    form.formID.studentSupervisee.ID,
                                    form.formID.termCode.termName,
                                    form.formID.department.DEPT_NAME,
                                    form.formID.supervisor.FIRST_NAME + " " + form.formID.supervisor.LAST_NAME,
                                    form.formID.supervisor.EMAIL,
                                    form.formID.jobType,
                                    form.formID.POSN_TITLE,
                                    form.formID.POSN_CODE,
                                    form.formID.WLS,
                                    form.formID.weeklyHours,
                                    form.formID.contractHours,
                                    form.formID.startDate,
                                    form.formID.endDate,
                                    form.status.statusName,
                                    form.formID.supervisorNotes]

                evaluation = StudentLaborEvaluation.get_or_none(StudentLaborEvaluation.formHistoryID == form.formHistoryID)
                if evaluation:
                    row.extend([str(evaluation.attendance_score),
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
                    # Include the summed overall score
                    row.append( evaluation.attendance_score +
                                evaluation.accountability_score +
                                evaluation.teamwork_score +
                                evaluation.initiative_score +
                                evaluation.respect_score +
                                evaluation.learning_score +
                                evaluation.jobSpecific_score
                                )
                filewriter.writerow(row)
        return self.relativePath;

    def makeExcelAllPendingForms(self, pendingForms):
        '''
        Creates a CSV of all pending forms
        '''
        with open(self.completePath, 'w') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=',',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
        ## Create heading on csv ##
            filewriter.writerow(['Student Name',
                                'Student Email',
                                'B#',
                                'Labor Position Title',
                                'Labor Position Code',
                                'Supervisor',
                                'Supervisor Email',
                                'Department',
                                'WLS',
                                'Weekly Hours',
                                'Total Contract Hours',
                                'Term',
                                'Start Date',
                                'End Date',
                                'Position',
                                'Supervisor Notes'])
        ## fill infomations ##
            for form in pendingForms:
                weeklyHours = form.formID.weeklyHours
                contractHours = form.formID.contractHours
                supervisor = form.formID.supervisor.FIRST_NAME + " " + form.formID.supervisor.LAST_NAME
                position = form.formID.POSN_TITLE
                positionCode = form.formID.POSN_CODE
                positionWLS = form.formID.WLS

                if form.historyType.historyTypeName == "Labor Adjustment Form":
                    if form.adjustedForm.fieldAdjusted == "weeklyHours":
                        weeklyHours = form.adjustedForm.newValue
                    if form.adjustedForm.fieldAdjusted == "contractHours":
                        contractHours = form.adjustedForm.newValue
                    if form.adjustedForm.fieldAdjusted == "supervisor":
                        newSupervisorID = form.adjustedForm.newValue
                        newSupervisor = Supervisor.get(Supervisor.ID == newSupervisorID)
                        supervisor = newSupervisor.FIRST_NAME +" "+ newSupervisor.LAST_NAME
                    if form.adjustedForm.fieldAdjusted == "position":
                        newPositionCode = form.adjustedForm.newValue
                        newPosition = Tracy().getPositionFromCode(newPositionCode)
                        position = newPosition.POSN_TITLE
                        positionCode = newPosition.POSN_CODE
                        positionWLS = newPosition.WLS

                filewriter.writerow([form.formID.studentSupervisee.FIRST_NAME + " " + form.formID.studentSupervisee.LAST_NAME,
                                    form.formID.studentSupervisee.STU_EMAIL,
                                    form.formID.studentSupervisee.ID,
                                    position,
                                    positionCode,
                                    supervisor,
                                    form.formID.supervisor.EMAIL,
                                    form.formID.department.DEPT_NAME,
                                    positionWLS,
                                    weeklyHours,
                                    contractHours,
                                    form.formID.termCode.termName,
                                    form.formID.startDate,
                                    form.formID.endDate,
                                    form.formID.jobType,
                                    form.formID.supervisorNotes])
        return self.relativePath;

    def makeList(self, student):
        '''
        Creates the CSV from the list of students in both "My Students" and "Department Students"
        '''
        downloadForms = []
        for id in student:
            studentForms = FormHistory.select().where(FormHistory.formID == id, FormHistory.historyType == 'Labor Status Form')
            for studentF in studentForms:
                downloadForms.append(studentF)

        with open(self.completePath, 'w') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=',',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)

        ## Create heading on csv ##
            filewriter.writerow(['Student Name',
                                 'Student Email',
                                'B#',
                                'Labor Position Title',
                                'Labor Position Code',
                                'Supervisor',
                                'Supervisor Email',
                                'Department',
                                'WLS',
                                'Weekly Hours',
                                'Total Contract Hours',
                                'Term',
                                'Start Date',
                                'End Date',
                                'Position',
                                'Form Status',
                                'Supervisor Notes',
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
        ## fill infomations ##
            for form in downloadForms:
                row = [ form.formID.studentSupervisee.FIRST_NAME + " " + form.formID.studentSupervisee.LAST_NAME,
                        form.formID.studentSupervisee.STU_EMAIL,
                        form.formID.studentSupervisee.ID,
                        form.formID.POSN_TITLE,
                        form.formID.POSN_CODE,
                        form.formID.supervisor.FIRST_NAME + " " + form.formID.supervisor.LAST_NAME,
                        form.formID.supervisor.EMAIL,
                        form.formID.department.DEPT_NAME,
                        form.formID.WLS,
                        form.formID.weeklyHours,
                        form.formID.contractHours,
                        form.formID.termCode.termName,
                        form.formID.startDate,
                        form.formID.endDate,
                        form.formID.jobType,
                        form.status.statusName,
                        form.formID.supervisorNotes
                      ]
                evaluation = StudentLaborEvaluation.get_or_none(StudentLaborEvaluation.formHistoryID == form.formHistoryID)
                if evaluation:
                    row.extend([str(evaluation.attendance_score),
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
                    # Include the summed overall score
                    row.append( evaluation.attendance_score +
                                evaluation.accountability_score +
                                evaluation.teamwork_score +
                                evaluation.initiative_score +
                                evaluation.respect_score +
                                evaluation.learning_score +
                                evaluation.jobSpecific_score
                                )
                filewriter.writerow(row)
        return self.relativePath;

def main():
    ExcelMaker()
