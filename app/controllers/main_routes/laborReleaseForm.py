from app.controllers.main_routes import *
from app.models.user import *
from app.models.laborReleaseForm import *
from app.models.formHistory import *
from app.models.laborStatusForm import *
from flask_bootstrap import bootstrap_find_resource
from app.models.student import *
from app.models.department import *
from app.models.historyType import *
from app.models.user import *
from app.controllers.errors_routes.handlers import *
from app.login_manager import require_login
from flask import Flask, redirect, url_for, flash
from flask import request
from datetime import datetime, date
from app.logic.emailHandler import*

@main_bp.route('/laborReleaseForm/<laborStatusKey>', methods=['GET', 'POST'])

def laborReleaseForm(laborStatusKey):
    currentUser = require_login()
    if not currentUser:
        render_template("errors/403.html"), 403
    if not currentUser.isLaborAdmin:       # Not an admin
        if currentUser.student and not currentUser.supervisor:
            return redirect('/laborHistory/' + currentUser.student.ID)

    forms = LaborStatusForm.select().distinct().where(LaborStatusForm.laborStatusFormID == laborStatusKey)

    if(request.method == 'POST'):
        try:
            historyForms = FormHistory.select().where((FormHistory.formID == laborStatusKey) & (FormHistory.releaseForm != None))
            if historyForms:
                for form in historyForms:
                    if form.status.statusName != "Denied":
                        # If there is currently a pending labor release form for the labor status form
                        # then the user should not be able submit another one
                        message = "An error has occurred. {0} {1} already has a 'Pending' Labor Release Form.".format(historyForms[0].formID.studentSupervisee.FIRST_NAME, historyForms[0].formID.studentSupervisee.LAST_NAME)
                        flash(message, "danger")
                        return redirect(url_for("main.supervisorPortal"))
            # If the labor status form does not have a pending labor release form, then the user
            # will be able to submit a labor release form. This section will create the new
            # labor release form, and a new form in the form history table.
            laborStatusForiegnKey = LaborStatusForm.get(LaborStatusForm.laborStatusFormID == laborStatusKey)
            formHistoryID = FormHistory.get(FormHistory.formID == laborStatusKey) #need formHistoryID for emailHandler
            datepickerDate = request.form.get("date")
            releaseDate = datetime.strptime(datepickerDate, "%m/%d/%Y").strftime("%Y-%m-%d")
            releaseReason = request.form.get("notes")
            releaseCondition = request.form.get("condition")

            createLaborReleaseForm(currentUser, laborStatusForiegnKey, releaseDate, releaseCondition, releaseReason)

            email = emailHandler(formHistoryID.formHistoryID)
            email.laborReleaseFormSubmitted()
            # Once all the forms are created, the user gets redirected to the
            # home page and gets a flash message telling them the forms were
            # submiteds
            message = "Your Labor Release Form for {0} {1} has been submitted.".format(laborStatusForiegnKey.studentSupervisee.FIRST_NAME, laborStatusForiegnKey.studentSupervisee.LAST_NAME)
            flash(message, "success")
            return redirect(url_for("main.supervisorPortal"))

        except Exception as e:
            print("Error: ", e)
            message = "An error has occurred. Your Labor Release Form for {0} {1} was not submitted.".format(laborStatusForiegnKey.studentSupervisee.FIRST_NAME, laborStatusForiegnKey.studentSupervisee.LAST_NAME)
            flash(message, "danger")
            return redirect(url_for("main.supervisorPortal"))
    return render_template('main/laborReleaseForm.html',
				            title=('Labor Release Form'),
                            forms = forms
                          )

def createLaborReleaseForm(currentUser, laborStatusForiegnKey, releaseDate, releaseCondition, releaseReason, status="Pending", reviewedDate=None, reviewedBy=None):
    newLaborReleaseForm = LaborReleaseForm.create(
                                conditionAtRelease = releaseCondition,
                                releaseDate = releaseDate,
                                reasonForRelease = releaseReason
                                )
    historytype = HistoryType.get(HistoryType.historyTypeName == "Labor Release Form")
    status = Status.get(Status.statusName == status)
    newFormHistory = FormHistory.create(
                                formID = laborStatusForiegnKey.laborStatusFormID,
                                historyType = historytype.historyTypeName,
                                releaseForm = newLaborReleaseForm.laborReleaseFormID,
                                adjustedForm = None,
                                overloadForm = None,
                                createdBy = currentUser,
                                createdDate = date.today(),
                                reviewedDate = reviewedDate,
                                reviewedBy = reviewedBy,
                                status = status.statusName,
                                rejectReason = None
                                )
