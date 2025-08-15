import datetime

from flask import Blueprint, request, render_template, redirect, flash, abort, g
from peewee import DoesNotExist

from app.models.laborStatusForm import LaborStatusForm
from app.models.formHistory import FormHistory

from app.controllers.main_routes import main_bp

@main_bp.route('/studentResponse/confirm', methods=['GET'])
def confirm():
    token = request.args.get('token')

    # Find the form and make sure the logged in user matches the student on the form
    forms = (LaborStatusForm.select()
                            .join(FormHistory)
                            .where(LaborStatusForm.confirmationToken == token
                                   ,LaborStatusForm.studentSupervisee == g.currentUser.student))
    try:
        form = forms.get()
    except DoesNotExist as e:
        flash("This contract is invalid or has expired.", "danger")
        abort(404)

    if form.studentConfirmation is not None: # 3 possible values, True, False, None
        verb = "accepted" if form.studentConfirmation else "denied"
        flash("This contract has already been " + verb + ".", "danger")
        abort(403)

    laborDescription = {
        "student_name": form.studentSupervisee.FIRST_NAME + " " + form.studentSupervisee.LAST_NAME,
        "expiration_date": form.studentExpirationDate,
        "student_id": form.studentSupervisee.ID,
        "supervisor": form.supervisor.FIRST_NAME + " " + form.supervisor.LAST_NAME,
        "position_code_title": f"{form.POSN_CODE}, {form.POSN_TITLE}",
        "wls": form.WLS,
        "jobType": form.jobType,
        "term": form.termCode,
        "department": form.department.DEPT_NAME,
        "hours_per_week": form.weeklyHours or form.contractHours,
        "start_date": form.startDate.strftime('%m/%d/%Y'),
        "end_date": form.endDate.strftime('%m/%d/%Y'),
    }

    return render_template('main/studentEmailConfirmation.html', form=form, laborDescription=laborDescription)

@main_bp.route('/studentResponse/submit', methods=['POST'])
def confirmSubmit():
    token = request.form.get('token')
    response = request.form.get('response')  # "Accepted" or "Denied" work contract
    checkbox = request.form.get('confirmParticipation') 

    if response == "Accepted" and checkbox == "0":
        # for some reason this flash is not showing -BR
        flash("You must agree to all terms before approving.", "danger")
        return redirect(request.referrer)  
    
    form = LaborStatusForm.get_or_none(LaborStatusForm.confirmationToken == token)
    if not form:
        flash("Invalid confirmation link", "danger")
        abort(404)

    form.studentConfirmation = (response == "Accepted")
    form.studentResponseDate = datetime.date.today()
    form.save()

    formHistory = FormHistory.get_or_none(FormHistory.formID == form.laborStatusFormID)

    msg = ""
    if response == "Accepted":
        formHistory.status = "Pending"
        msg = "You have accepted this form."
    else:
        formHistory.status = "Denied by Student"
        msg = "You have denied this form."
        # TODO do we need to email about the denial?
    
    formHistory.save()
        
    flash("Thank you for your response. " + msg, "success")
    return redirect('/')
