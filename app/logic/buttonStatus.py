from enum import Enum
from datetime import date
from app.logic.search import getDepartmentsForSupervisor
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
        self.resubmit = False
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

    def set_button_states(self, historyForm, currentUser):
        ############################################################
        # Student Options
        ############################################################
        if currentUser.student and currentUser.student.ID == historyForm.formID.studentSupervisee.ID:
            # students get no buttons
            self.rehire = False
            self.release = False
            self.withdraw = False
            self.adjust = False
            self.correction = False
            self.resubmit = False
            self.num_buttons = 1

        ############################################################
        # Labor Admin and Supervisor Options
        ############################################################
        else:
            #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            # Release
            #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            if historyForm.releaseForm:
                if historyForm.status.statusName == "Approved":
                    self.rehire = True
                    self.resubmit = True
                    self.num_buttons += 2

                elif "Denied" in historyForm.status.statusName:
                    self.rehire = True
                    self.release = True
                    self.adjust = True
                    self.num_buttons += 3

                elif historyForm.status.statusName == "Pending":
                    # Pending release forms get no buttons
                    pass

            #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            # Adjustment
            #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            elif historyForm.adjustedForm:
                if historyForm.status.statusName in ["Approved","Denied by Student","Denied by Admin"]:
                    self.rehire = True
                    self.release = True
                    self.adjust = True
                    self.num_buttons += 3
                # Pending adjustment forms get no buttons

            #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            # Standard or Overload
            #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            elif historyForm.historyType.historyTypeName in ["Labor Status Form", "Labor Overload Form"]:
                if historyForm.status.statusName in ["Pending","Pre-Student Approval"]:
                    # Pending LSF can be withdrawn or corrected
                    self.withdraw = True
                    self.correction = True
                    self.num_buttons += 2

                elif "Denied" in historyForm.status.statusName: # handle both denies
                    # Denied LSF forms can be rehired
                    self.rehire = True
                    self.num_buttons += 1

                elif historyForm.status.statusName == "Approved":
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
                            self.resubmit = True
                            self.num_buttons += 4
                    else:
                        self.rehire = True
                        self.num_buttons += 1
