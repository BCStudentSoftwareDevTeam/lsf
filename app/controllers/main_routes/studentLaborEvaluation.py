from app.controllers.main_routes import *
from app.login_manager import *
import app.login_manager as login_manager
from flask import redirect, flash
from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, TextAreaField
from wtforms.fields.html5 import IntegerRangeField
from wtforms.validators import DataRequired
from app.models.formHistory import *
from app.models.studentLaborEvaluation import StudentLaborEvaluation


class SLEForm(FlaskForm):

    attendance = IntegerRangeField("Attendence", render_kw={'class':'form-control slider'})
    attendanceComments = TextAreaField("Comments about attendance:", render_kw={'class':'form-control'})

    accountability = IntegerRangeField("Accountability", render_kw={'class':'form-control slider'})
    accountabilityComments = TextAreaField("Comments about accountability:", render_kw={'class':'form-control'})

    teamwork = IntegerRangeField("Teamwork", render_kw={'class':'form-control slider'})
    teamworkComments = TextAreaField("Comments about teamwork:", render_kw={'class':'form-control'})

    initiative = IntegerRangeField("Initiative", render_kw={'class':'form-control slider'})
    initiativeComments = TextAreaField("Comments about initiative:", render_kw={'class':'form-control'})

    respect  = IntegerRangeField("Respect", render_kw={'class':'form-control slider'})
    respectComments = TextAreaField("Comments about respect:", render_kw={'class':'form-control'})

    learning = IntegerRangeField("Learning", render_kw={'class':'form-control slider'})
    learningComments = TextAreaField("Comments about learning:", render_kw={'class':'form-control'})

    jobSpecific = IntegerRangeField("Job Specific", render_kw={'class':'form-control slider'})
    jobSpecificComments = TextAreaField("Comments about this job, specifically:", render_kw={'class':'form-control'})


@main_bp.route('/sle/<statusKey>', methods=['GET', 'POST'])
def sle(statusKey):
    # NOTE: statusKey is the LSF id. Everything after this (template and controller) uses the associated laborHistory object/ID for this LSF id.
    currentUser = require_login()
    # print("Status key: ", statusKey)
    laborHistoryForm = FormHistory.select().where((FormHistory.formID == int(statusKey))).where(FormHistory.historyType == "Labor Status Form")[-1]

    if currentUser.supervisor != laborHistoryForm.formID.supervisor:
        # current user is not the supervisor
        return render_template('errors/403.html'), 403
    existing_evaluation = StudentLaborEvaluation.get_or_none(formHistoryID = laborHistoryForm)
    if not laborHistoryForm.formID.termCode.isFinalEvaluationOpen and not existing_evaluation:
        return render_template('errors/403.html'), 403
    if existing_evaluation:
        overall_score = (existing_evaluation.attendance_score +
                        existing_evaluation.accountability_score +
                        existing_evaluation.teamwork_score +
                        existing_evaluation.initiative_score +
                        existing_evaluation.respect_score +
                        existing_evaluation.learning_score +
                        existing_evaluation.jobSpecific_score)
    else:
        overall_score = 73      # The default value
    sleForm = SLEForm()
    if sleForm.validate_on_submit():
        studentLaborEvaluation = StudentLaborEvaluation.create(
                                    formHistoryID = laborHistoryForm,
                                    attendance_score = sleForm.attendance.data,
                                    attendance_comment = sleForm.attendanceComments.data,
                                    accountability_score = sleForm.accountability.data,
                                    accountability_comment = sleForm.accountabilityComments.data,
                                    teamwork_score = sleForm.teamwork.data,
                                    teamwork_comment = sleForm.teamworkComments.data,
                                    initiative_score = sleForm.initiative.data,
                                    initiative_comment = sleForm.initiativeComments.data,
                                    respect_score = sleForm.respect.data,
                                    respect_comment = sleForm.respectComments.data,
                                    learning_score = sleForm.learning.data,
                                    learning_comment = sleForm.learningComments.data,
                                    jobSpecific_score = sleForm.jobSpecific.data,
                                    jobSpecific_comment = sleForm.jobSpecificComments.data
                                )
        studentLaborEvaluation.save()
        msg = "Thank you for submitting a labor evaluation for " + laborHistoryForm.formID.studentName + "!"
        flash(msg, "success")
        return redirect("/")

    if laborHistoryForm.status.statusName != "Approved":
        # Only approved evaluations get an SLE, so send them home.
        return redirect("/")

    return render_template("main/studentLaborEvaluation.html",
                            form = sleForm,
                            laborHistoryForm = laborHistoryForm,
                            existing_evaluation = existing_evaluation,
                            overall_score = overall_score
                          )
