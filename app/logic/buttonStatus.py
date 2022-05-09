from enum import Enum
from datetime import date
from app.models.studentLaborEvaluation import StudentLaborEvaluation
from app.models.formHistory import FormHistory
from app.logic.tracy import Tracy, InvalidQueryException

class ButtonStatus:
    def __init__(self):
        self.currentDate = date.today()
        self.rehire = False
        self.release = False
        self.withdraw = False
        self.adjust = False
        self.correction = False
        self.evaluate = False
        self.evaluation_exists = False
        self.num_buttons = 0

    def get_history_form_from_lsf(self, historyForm):
        '''
        Given any form history object, retrieves the correct form history
        for the original LSF. This is useful for getting the correct form history
        ID when you have a release or adjustment form as the last submitted form.

        param historyForm: a form history object

        return: a form history object representing the original LSF form
        '''
        return FormHistory.get(FormHistory.formID == historyForm.formID, FormHistory.status == "Approved", FormHistory.historyType == "Labor Status Form")

    def set_evaluation_button(self, historyForm, currentUser, isActiveStudent = True):
        ogHistoryForm = self.get_history_form_from_lsf(historyForm)
        if not isActiveStudent:
            # Only grab final evaluations for students no longer at the college
            evaluations = StudentLaborEvaluation.select().where(StudentLaborEvaluation.formHistoryID == ogHistoryForm, StudentLaborEvaluation.is_submitted == True, StudentLaborEvaluation.is_midyear_evaluation == False)
        else:
            evaluations = StudentLaborEvaluation.select().where(StudentLaborEvaluation.formHistoryID == ogHistoryForm, StudentLaborEvaluation.is_submitted == True)

        if currentUser.student:
            for evaluation in evaluations:
                if evaluation.is_midyear_evaluation and not historyForm.formID.termCode.isFinalEvaluationOpen:
                    self.evaluation_exists = True
                    self.num_buttons += 1
                elif not evaluation.is_midyear_evaluation:  #i.e., it's a final evaluation
                    self.evaluation_exists = True
                    self.num_buttons += 1
        else:
            if ogHistoryForm.formID.supervisor.DEPT_NAME == currentUser.supervisor.DEPT_NAME:
                if historyForm.formID.termCode.isFinalEvaluationOpen or historyForm.formID.termCode.isMidyearEvaluationOpen:
                    self.evaluate = True
                    self.num_buttons += 1
                for evaluation in evaluations:
                    if evaluation.is_midyear_evaluation and not historyForm.formID.termCode.isFinalEvaluationOpen:
                        # If a midyear evaluation has been completed
                        self.evaluation_exists = True
                        self.evaluate = False
                        self.num_buttons += 1
                    elif not evaluation.is_midyear_evaluation:
                        # If a final labor evaluation has been completed
                        self.evaluation_exists = True
                        self.evaluate = False
                        self.num_buttons += 1

    def set_button_states(self, historyForm, currentUser):
        try:
            tracyObj = Tracy()
            isActiveStudent = True if tracyObj.getStudentFromBNumber(historyForm.formID.studentSupervisee.ID) else False
        except InvalidQueryException:
            isActiveStudent = False

        if not isActiveStudent:     # Student on the form is no longer at the college
            # TODO: No buttons except evaluation if it exists
            self.set_evaluation_button( historyForm, currentUser, isActiveStudent = False)

        elif currentUser.student and currentUser.student.ID == historyForm.formID.studentSupervisee.ID:
            # students get no buttons except "show evaluation"
            self.rehire = False
            self.release = False
            self.withdraw = False
            self.adjust = False
            self.correction = False
            self.evaluate = False
            self.set_evaluation_button( historyForm, currentUser)
            self.num_buttons = 1

        else:
            if historyForm.releaseForm != None:     # If its a release form
                if historyForm.status.statusName == "Approved":
                    # Approved release forms can be rehired
                    self.rehire = True
                    if historyForm.formID.supervisor.ID == currentUser.supervisor.ID:
                        self.set_evaluation_button(historyForm, currentUser)
                    self.num_buttons += 2
                elif historyForm.status.statusName == "Denied":
                    self.rehire = True
                    self.release = True
                    self.adjust = True
                    if historyForm.formID.supervisor.ID == currentUser.supervisor.ID:
                        self.set_evaluation_button(historyForm, currentUser)
                    self.num_buttons += 4
                elif historyForm.status.statusName == "Pending":
                    # Pending release forms get no buttons
                    pass
            elif historyForm.adjustedForm != None:    # If its an adjustment form
                if historyForm.status.statusName == "Approved" or historyForm.status.statusName == "Denied":
                    self.rehire = True
                    self.release = True
                    self.adjust = True
                    if historyForm.formID.supervisor.ID == currentUser.supervisor.ID:
                        self.set_evaluation_button(historyForm, currentUser)
                    self.num_buttons += 4
                elif historyForm.status.statusName == "Pending":
                    # Pending adjustment forms get no buttons
                    pass
            elif historyForm.historyType.historyTypeName == "Labor Status Form":
                if historyForm.status.statusName == "Pending":
                    # Pending LSF can be withdrawn or corrected
                    self.withdraw = True
                    self.correction = True
                    self.num_buttons += 2
                elif historyForm.status.statusName == "Denied":
                    # Denied LSF forms can be rehired
                    self.rehire = True
                    self.num_buttons += 1
                elif historyForm.status.statusName == "Approved":
                    self.set_evaluation_button(historyForm, currentUser)
                    self.num_buttons += 1
                    if self.currentDate <= historyForm.formID.endDate:
                        # An approved LSF before the end of the term
                        if self.currentDate > historyForm.formID.termCode.adjustmentCutOff and not currentUser.isLaborAdmin:
                            # An approved LSF after the adjustment cutoff date, non-admin
                            self.release = True
                            self.rehire = True
                            self.num_buttons += 2
                        else:
                            # Admin, or before adjustment cutoff date
                            self.release = True
                            self.adjust = True
                            self.rehire = True
                            self.num_buttons += 3
                    else:
                        self.rehire = True
                        self.num_buttons += 1
