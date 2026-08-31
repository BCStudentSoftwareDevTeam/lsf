from app.controllers.main_routes import *
from app.login_manager import *
import app.login_manager as login_manager
from flask import redirect, flash
from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, TextAreaField, HiddenField, BooleanField
from wtforms.fields import IntegerRangeField
from wtforms.validators import DataRequired, Length
from app.models.formHistory import *
from app.models.studentLaborEvaluation import StudentLaborEvaluation
from werkzeug.exceptions import BadRequestKeyError
from app.logic.search import getDepartmentsForSupervisor
from datetime import date

class SLEForm(FlaskForm):

    attendance = IntegerRangeField("Attendance", default = 15, render_kw={'class':'form-control slider'})
    attendanceComments = TextAreaField("Comments about attendance:", [Length(max=65535)], render_kw={'class':'form-control'})

    accountability = IntegerRangeField("Accountability", default = 7, render_kw={'class':'form-control slider'})
    accountabilityComments = TextAreaField("Comments about accountability:", [Length(max=65535)], render_kw={'class':'form-control'})

    teamwork = IntegerRangeField("Teamwork", default = 7, render_kw={'class':'form-control slider'})
    teamworkComments = TextAreaField("Comments about teamwork:", [Length(max=65535)], render_kw={'class':'form-control'})

    initiative = IntegerRangeField("Initiative", default = 7, render_kw={'class':'form-control slider'})
    initiativeComments = TextAreaField("Comments about initiative:", [Length(max=65535)], render_kw={'class':'form-control'})

    respect  = IntegerRangeField("Respect", default = 7, render_kw={'class':'form-control slider'})
    respectComments = TextAreaField("Comments about respect:", [Length(max=65535)], render_kw={'class':'form-control'})

    learning = IntegerRangeField("Learning", default = 15, render_kw={'class':'form-control slider'})
    learningComments = TextAreaField("Comments about learning:", [Length(max=65535)], render_kw={'class':'form-control'})

    jobSpecific = IntegerRangeField("Job Specific", default = 15, render_kw={'class':'form-control slider'})
    jobSpecificComments = TextAreaField("Comments about this job, specifically:", [Length(max=65535)], render_kw={'class':'form-control'})

    transcriptComments = TextAreaField("Labor Transcript comments:", [Length(max=65535)], render_kw={'class':'form-control'})

    isSubmitted = HiddenField('Is this a final submission', default = False)


@main_bp.route('/sle/<statusKey>', methods=['GET', 'POST'])
def sle(statusKey):
    # NOTE: statusKey is the LSF id. Everything after this (template and controller) uses the associated laborHistory object/ID for this LSF id.
    currentUser = require_login()

    laborHistoryForm = FormHistory.select().where((FormHistory.formID == int(statusKey))).where(FormHistory.historyType == "Labor Status Form")[-1]
    if request.form.get("resetConfirmation"):
        # Delete the most recently submitted evaluation for this formhistory
        newest = (StudentLaborEvaluation.select()
                    .where(StudentLaborEvaluation.formHistoryID == laborHistoryForm.formHistoryID)
                    .order_by(StudentLaborEvaluation.date_submitted.desc(nulls="LAST"), StudentLaborEvaluation.ID.desc())
                    ).get()
        if newest:
            newest.delete_instance()

        return redirect("/sle/" + str(laborHistoryForm.formID.laborStatusFormID))

    if currentUser.student and currentUser.student.ID != laborHistoryForm.formID.studentSupervisee.ID:
        # current user is not the student
        return render_template('errors/403.html'), 403

    elif not currentUser.isLaborAdmin and laborHistoryForm.formID.supervisor.DEPT_NAME not in [dept.DEPT_NAME for dept in getDepartmentsForSupervisor(currentUser)]:
        # current user is not in the same dept as the lsf supervisor
        return render_template('errors/403.html'), 403

    sleForm = SLEForm()
    existing_evaluation = (StudentLaborEvaluation.select()
                            .where(StudentLaborEvaluation.formHistoryID == laborHistoryForm, StudentLaborEvaluation.is_submitted == True)
                            .order_by(StudentLaborEvaluation.date_submitted.desc(nulls="LAST"), StudentLaborEvaluation.ID.desc())
                            .first())
    existing_saved_evaluation = StudentLaborEvaluation.select().where(StudentLaborEvaluation.formHistoryID == laborHistoryForm, StudentLaborEvaluation.is_submitted == False)
    if existing_saved_evaluation:
        existing_saved_evaluation = existing_saved_evaluation[-1]

    if not request.method == "POST":        # Doesn't override submitted POST data!
        if existing_saved_evaluation:
            sleForm.attendance.data = existing_saved_evaluation.attendance_score
            sleForm.accountability.data = existing_saved_evaluation.accountability_score
            sleForm.teamwork.data = existing_saved_evaluation.teamwork_score
            sleForm.initiative.data = existing_saved_evaluation.initiative_score
            sleForm.respect.data = existing_saved_evaluation.respect_score
            sleForm.learning.data = existing_saved_evaluation.learning_score
            sleForm.jobSpecific.data = existing_saved_evaluation.jobSpecific_score

            sleForm.attendanceComments.data = existing_saved_evaluation.attendance_comment
            sleForm.accountabilityComments.data = existing_saved_evaluation.accountability_comment
            sleForm.teamworkComments.data = existing_saved_evaluation.teamwork_comment
            sleForm.initiativeComments.data = existing_saved_evaluation.initiative_comment
            sleForm.respectComments.data = existing_saved_evaluation.respect_comment
            sleForm.learningComments.data = existing_saved_evaluation.learning_comment
            sleForm.jobSpecificComments.data = existing_saved_evaluation.jobSpecific_comment
            sleForm.transcriptComments.data = existing_saved_evaluation.transcript_comment

    overall_score = 73      # The default value
    if existing_evaluation:
        overall_score = (existing_evaluation.attendance_score +
                        existing_evaluation.accountability_score +
                        existing_evaluation.teamwork_score +
                        existing_evaluation.initiative_score +
                        existing_evaluation.respect_score +
                        existing_evaluation.learning_score +
                        existing_evaluation.jobSpecific_score)

    if sleForm.validate_on_submit():
        try:
            sle = StudentLaborEvaluation.get(formHistoryID = laborHistoryForm, is_submitted = False)
            sle.delete_instance()
        except DoesNotExist:
            pass

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
                                    jobSpecific_comment = sleForm.jobSpecificComments.data,
                                    transcript_comment = sleForm.transcriptComments.data,
                                    is_submitted = True if sleForm.isSubmitted.data == "True" else False,
                                    submitted_by = currentUser,
                                    date_submitted = date.today()
                                )
        studentLaborEvaluation.save()
        msg = f"Thank you for submitting a labor evaluation for {laborHistoryForm.formID.studentSupervisee.FIRST_NAME} {laborHistoryForm.formID.studentSupervisee.LAST_NAME}!"
        flash(msg, "success")
        return redirect("/")

    if laborHistoryForm.status.statusName != "Approved":
        # Only approved evaluations get an SLE, so send them home.
        return redirect("/")

    if existing_evaluation and existing_evaluation.date_submitted:
        submittedDate = existing_evaluation.date_submitted.strftime("%m-%d-%Y")
    else:
        submittedDate = None

    return render_template("main/studentLaborEvaluation.html",
                            form = sleForm,
                            laborHistoryForm = laborHistoryForm,
                            existing_evaluation = existing_evaluation,
                            date_submitted = submittedDate,
                            overall_score = overall_score,
                            currentUser = currentUser
                          )
