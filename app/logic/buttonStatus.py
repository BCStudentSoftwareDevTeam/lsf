from enum import Enum
from datetime import date
from app.logic.search import getDepartmentsForSupervisor
from app.models.studentLaborEvaluation import StudentLaborEvaluation
from app.models.formHistory import FormHistory

class ButtonStatus:
    # show_rehire_button = 0
    # show_withdraw_button = 1
    # show_withdraw_correction_buttons = 2
    # show_release_adjustment_rehire_buttons = 3
    # show_release_rehire_buttons = 4
    # no_buttons_pending_forms = 5
    # show_student_view = 6

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
        return FormHistory.get(FormHistory.formID == historyForm.formID, (FormHistory.status == "Approved") | (FormHistory.status == "Pending"), FormHistory.historyType == "Labor Status Form")

    def set_evaluation_button(self, historyForm, currentUser):
        ogHistoryForm = self.get_history_form_from_lsf(historyForm)
        evaluations = StudentLaborEvaluation.select().where(StudentLaborEvaluation.formHistoryID == ogHistoryForm, StudentLaborEvaluation.is_submitted == True)
        if currentUser.student:
            for evaluation in evaluations:

                if evaluation.is_midyear_evaluation and not historyForm.formID.termCode.isFinalEvaluationOpen:
                    self.evaluation_exists = True
                elif not evaluation.is_midyear_evaluation:  #i.e., it's a final evaluation
                    self.evaluation_exists = True
        else:
            currentUserDepartments = [department.DEPT_NAME for department in getDepartmentsForSupervisor(currentUser)]
            if ogHistoryForm.formID.supervisor.DEPT_NAME in currentUserDepartments or currentUser.isLaborAdmin:
                if historyForm.formID.termCode.isFinalEvaluationOpen or historyForm.formID.termCode.isMidyearEvaluationOpen:
                    self.evaluate = True
                for evaluation in evaluations:
                    if evaluation.is_midyear_evaluation and not historyForm.formID.termCode.isFinalEvaluationOpen:
                        # If a midyear evaluation has been completed
                        self.evaluation_exists = True
                        self.evaluate = False
                    elif not evaluation.is_midyear_evaluation:
                        # If a final labor evaluation has been completed
                        self.evaluation_exists = True
                        self.evaluate = False

    def set_button_states(self, historyForm, currentUser):
        ############################################################
        # Student Options
        ############################################################
        if currentUser.student and currentUser.student.ID == historyForm.formID.studentSupervisee.ID:

            # students get no buttons except "show evaluation"
            if historyForm.historyType.historyTypeName == "Labor Status Form" or historyForm.historyType.historyTypeName == "Labor Overload Form" :
                if historyForm.status.statusName == "Pending" or historyForm.status.statusName == "Pre-Student Approval":
                    self.withdraw = True
                    self.num_buttons = 1
            else:
                self.rehire = False
                self.release = False
                self.withdraw = False
                self.adjust = False
                self.correction = False
                self.evaluate = False
                self.set_evaluation_button( historyForm, currentUser)
                self.num_buttons = 1

        ############################################################
        # Labor Admin and Supervisor Options
        ############################################################
        else:
            #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            # Release
            #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            if historyForm.releaseForm != None:
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

            #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            # Adjustment
            #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            elif historyForm.adjustedForm != None:
                if historyForm.status.statusName in ["Approved","Denied"]:
                    self.rehire = True
                    self.release = True
                    self.adjust = True

                    if currentUser.isLaborAdmin or historyForm.formID.supervisor.ID == currentUser.supervisor.ID:
                        self.set_evaluation_button(historyForm, currentUser)
                    self.num_buttons += 4

                elif historyForm.status.statusName == "Pending":
                    # Pending adjustment forms get no buttons
                    if historyForm.formID.supervisor.ID == currentUser.supervisor.ID:
                        self.set_evaluation_button(historyForm, currentUser)
                    self.num_buttons += 1

            #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            # Standard or Overload
            #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            elif historyForm.historyType.historyTypeName in ["Labor Status Form", "Labor Overload Form"]:
                if historyForm.status.statusName in ["Pending","Pre-Student Approval"]:
                    # Pending LSF can be withdrawn or corrected
                    self.withdraw = True
                    self.correction = True
                    self.num_buttons += 2

                elif historyForm.status.statusName == "Denied":
                    # Denied LSF forms can be rehired
                    self.rehire = True
                    self.num_buttons += 1

                elif historyForm.status.statusName in ["Approved","Approved Reluctantly"]:
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
