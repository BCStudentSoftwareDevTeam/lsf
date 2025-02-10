from flask import Blueprint, request, render_template, redirect, flash
from datetime import date
from app.models.laborStatusForm import LaborStatusForm
from app.models.formHistory import FormHistory
import datetime

from app.controllers.main_routes import *

@main_bp.route('/studentResponse/confirm', methods=['GET'])
def confirm():
    token = request.args.get('token')
    form = LaborStatusForm.get_or_none(LaborStatusForm.confirmationToken == token)

    if not form:
        flash("Invalid confirmation link", "danger")
        return render_template('errors/404.html'), 404

    laborDescription = {
        "student_name": form.studentSupervisee.FIRST_NAME + " " + form.studentSupervisee.LAST_NAME,
        "student_id": form.studentSupervisee.ID,
        "supervisor": form.supervisor.FIRST_NAME + " " + form.supervisor.LAST_NAME,
        "position_code_title": f"{form.POSN_CODE}, {form.POSN_TITLE}",
        "wls": form.WLS,
        "department": form.department.DEPT_NAME,
        "hours_per_week": form.weeklyHours or form.contractHours,
        "start_date": form.startDate.strftime('%m/%d/%Y'),
    }

    return render_template('main/studentEmailConfirmation.html', form=form, laborDescription=laborDescription)

@main_bp.route('/studentResponse/submit', methods=['POST'])
def confirmSubmit():
    token = request.form.get('token')
    response = request.form.get('response')  # "Accepted" or "Denied" work contract
    form = LaborStatusForm.get_or_none(LaborStatusForm.confirmationToken == token)

    if not form:
        flash("Invalid confirmation link", "danger")
        return render_template('errors/404.html'), 404

    form.studentConfirmation = True if response == "Accepted" else False
    form.studentResponseDate = datetime.date.today()
    form.save()

    formHistory = FormHistory.get_or_none(FormHistory.formID == form.laborStatusFormID)

    if not formHistory:
        FormHistory.create(formID=form.laborStatusFormID, status="Pre-Student Approval")

    if response == "Accepted":
        formHistory.status = "Pending"
        formHistory.save()

        FormHistory.delete().where(FormHistory.formID == form.laborStatusFormID, FormHistory.status == "Pre-Student Approval").execute()
    else:
        formHistory.status = "Pre-Student Approval"
        formHistory.save()
        
    
    flash("Thank you for your response.", "success")
    return redirect('/')

@main_bp.route('/studentResponse/confirmationResponse', methods=['GET'])
def confirmationResponse():
    return render_template('main/confirmationResponse.html')