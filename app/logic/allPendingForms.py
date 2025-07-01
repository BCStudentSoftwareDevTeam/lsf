import json
from datetime import date
from flask import jsonify
from app.models.formHistory import FormHistory
from app.models.status import Status
from app.logic.banner import Banner
from app.logic.emailHandler import emailHandler
from app.login_manager import require_login
from app.models.laborStatusForm import LaborStatusForm
from app.models.supervisor import Supervisor
from app.models.department import Department
from app.logic.userInsertFunctions import createSupervisorFromTracy
from app.logic.tracy import Tracy
from app.




def saveStatus(new_status, form_ids, currentUser):
    try:
        if new_status == 'Denied by Admin':
            # Index 1 will always hold the reject reason in the list, so we can
            # set a variable equal to the index value and then slice off the list
            # item before the iteration
            denyReason = form_ids[1]
            form_ids = form_ids[:1]
        for id in form_ids:
            history_type_data = FormHistory.get(FormHistory.formHistoryID == int(id))
            history_type = str(history_type_data.historyType)

            labor_forms = FormHistory.get(FormHistory.formHistoryID == int(id), FormHistory.historyType == history_type)
            labor_forms.status = Status.get(Status.statusName == new_status)
            
            labor_forms.reviewedDate = date.today()
            labor_forms.reviewedBy = currentUser

            # Add to BANNER
            save_status = True # default true so that we will still save in other cases
            if new_status == 'Approved' and history_type == "Labor Status Form" and labor_forms.formID.POSN_CODE != "S12345": # don't update banner for Adjustment forms or for CS dummy position
                if labor_forms.formID.POSN_CODE == "SNOLAB":
                       labor_forms.formID.weeklyHours = 10
                conn = Banner()
                save_status = conn.insert(labor_forms)

            # if we are able to save
            if save_status:

                if new_status == 'Denied by Admin':
                    labor_forms.rejectReason = denyReason
                labor_forms.save()

                email = emailHandler(labor_forms.formHistoryID)
                if new_status == "Denied by Admin" and history_type == "Labor Status Form":
                    email.laborStatusFormRejected()
                if new_status == "Approved" and history_type == "Labor Status Form":
                    email.laborStatusFormApproved()
                if new_status == "Approved" and history_type == "Labor Adjustment Form":
                    # This function is triggered whenever an adjustment form is approved.
                    # The following function overrides the original data in lsf with the new data from adjustment form.
                    LSF = LaborStatusForm.get(LaborStatusForm.laborStatusFormID == history_type_data.formID) # getting the specific labor status form
                    overrideOriginalStatusFormOnAdjustmentFormApproval(history_type_data, LSF)

            else:
                print("Unable to update form status for formHistoryID {}.".format(id))
                return jsonify({"success": False}), 500

    except Exception as e:
        print("Error preparing form for status update:", e)
        return jsonify({"success": False}), 500

    return jsonify({"success": True})

def overrideOriginalStatusFormOnAdjustmentFormApproval(form, LSF):
    """
    This function checks whether an Adjustment Form is approved. If yes, it overrides the information
    in the original Labor Status Form with the new information coming from approved Adjustment Form.

    The only fields that will ever be changed in an adjustment form are: supervisor, department, position, and hours.
    """
    currentUser = require_login()
    if not currentUser:        # Not logged in
            return render_template('errors/403.html'), 403
    if form.adjustedForm.fieldAdjusted == "supervisor":
        d, created = Supervisor.get_or_create(ID = form.adjustedForm.newValue)
        if not created:
            LSF.supervisor = d.ID
        LSF.save()
        if created:
            tracyUser = Tracy().getSupervisorFromID(form.adjustedForm.newValue)
            tracyEmail = tracyUser.EMAIL
            tracyUsername = tracyEmail.find('@')
            createSupervisorFromTracy(tracyUsername)

    if form.adjustedForm.fieldAdjusted == "position":
        LSF.POSN_CODE = form.adjustedForm.newValue
        position = Tracy().getPositionFromCode(form.adjustedForm.newValue)
        LSF.POSN_TITLE = position.POSN_TITLE
        LSF.WLS = position.WLS
        LSF.save()

    if form.adjustedForm.fieldAdjusted == "department":
        department = Department.get(Department.ORG==form.adjustedForm.newValue)
        LSF.department = department.departmentID
        LSF.save()

    if form.adjustedForm.fieldAdjusted == "contractHours":
        LSF.contractHours = int(form.adjustedForm.newValue)
        LSF.save()

    if form.adjustedForm.fieldAdjusted == "weeklyHours":
        LSF.weeklyHours = int(form.adjustedForm.newValue)
        LSF.save()