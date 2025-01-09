from flask import Blueprint, request, render_template, redirect, flash
from datetime import date
from app.models.laborStatusForm import LaborStatusForm
from app.models.formHistory import FormHistory

from app.controllers.main_routes import *

@main_bp.route('/studentResponse/confirm', methods=['GET'])
def confirm():
    token = request.args.get('token')
    form = LaborStatusForm.get_or_none(LaborStatusForm.confirmationToken == token)

    if not form:
        flash("Invalid confirmation link.", "danger")
        return render_template('errors/404.html'), 404

    return render_template('studentEmailConfirmation.html', form=form)

@main_bp.route('/studentResponse/submit', methods=['POST'])
def confirmSubmit():
    token = request.form.get('token')
    response = request.form.get('response')  # "Accepted" or "Denied"
    reason = request.form.get('reason') if response == "Denied" else None
    form = LaborStatusForm.get_or_none(LaborStatusForm.confirmationToken == token)

    if not form:
        flash("Invalid confirmation link.", "danger")
        return render_template('errors/404.html'), 404

    form.studentConfirmation = response
    form.studentResponseDate = date.today()
    form.studentRejection = reason
    form.save()
    return redirect("/studentResponse/confirmationResponse")

@main_bp.route('/studentResponse/confirmationResponse', methods=['GET'])
def confirmationResponse():
    return render_template('confirmationResponse.html')