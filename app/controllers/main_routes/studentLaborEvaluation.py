from app.controllers.main_routes import *
from app.login_manager import *
import app.login_manager as login_manager
from flask import redirect, flash
from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, TextAreaField, HiddenField
from wtforms.fields.html5 import IntegerRangeField
from wtforms.validators import DataRequired
from app.models.formHistory import *
from app.models.studentLaborEvaluation import StudentLaborEvaluation


class SLEForm(FlaskForm):

    attendance = IntegerRangeField("Attendance", default = 15, render_kw={'class':'form-control slider'})
    attendanceComments = TextAreaField("Comments about attendance:", render_kw={'class':'form-control'})
    attendanceCommentsMidyear = TextAreaField("Attendance comments from Midyear :", render_kw={'class':'form-control', 'readonly': True})

    accountability = IntegerRangeField("Accountability", default = 7, render_kw={'class':'form-control slider'})
    accountabilityComments = TextAreaField("Comments about accountability:", render_kw={'class':'form-control'})
    accountabilityCommentsMidyear = TextAreaField("Attendance comments from Midyear :", render_kw={'class':'form-control', 'readonly': True})

    teamwork = IntegerRangeField("Teamwork", default = 7, render_kw={'class':'form-control slider'})
    teamworkComments = TextAreaField("Comments about teamwork:", render_kw={'class':'form-control'})
    teamworkCommentsMidyear = TextAreaField("Attendance comments from Midyear :", render_kw={'class':'form-control', 'readonly': True})

    initiative = IntegerRangeField("Initiative", default = 7, render_kw={'class':'form-control slider'})
    initiativeComments = TextAreaField("Comments about initiative:", render_kw={'class':'form-control'})
    initiativeCommentsMidyear = TextAreaField("Attendance comments from Midyear :", render_kw={'class':'form-control', 'readonly': True})

    respect  = IntegerRangeField("Respect", default = 7, render_kw={'class':'form-control slider'})
    respectComments = TextAreaField("Comments about respect:", render_kw={'class':'form-control'})
    respectCommentsMidyear = TextAreaField("Attendance comments from Midyear :", render_kw={'class':'form-control', 'readonly': True})

    learning = IntegerRangeField("Learning", default = 15, render_kw={'class':'form-control slider'})
    learningComments = TextAreaField("Comments about learning:", render_kw={'class':'form-control'})
    learningCommentsMidyear = TextAreaField("Attendance comments from Midyear :", render_kw={'class':'form-control', 'readonly': True})

    jobSpecific = IntegerRangeField("Job Specific", default = 15, render_kw={'class':'form-control slider'})
    jobSpecificComments = TextAreaField("Comments about this job, specifically:", render_kw={'class':'form-control'})
    jobSpecificCommentsMidyear = TextAreaField("Attendance comments from Midyear :", render_kw={'class':'form-control', 'readonly': True})

    transcriptComments = TextAreaField("Labor Transcript comments:", render_kw={'class':'form-control'})

    isSubmitted = HiddenField('Is this a final submission', default = False)


@main_bp.route('/sle/<statusKey>', methods=['GET', 'POST'])
def sle(statusKey):
    # NOTE: statusKey is the LSF id. Everything after this (template and controller) uses the associated laborHistory object/ID for this LSF id.
    currentUser = require_login()

    laborHistoryForm = FormHistory.select().where((FormHistory.formID == int(statusKey))).where(FormHistory.historyType == "Labor Status Form")[-1]
    if currentUser.student and currentUser.student.ID != laborHistoryForm.formID.studentSupervisee.ID:
        # current user is not the supervisor
        return render_template('errors/403.html'), 403
    elif currentUser.student == None and currentUser.supervisor != laborHistoryForm.formID.supervisor:
        # current user is not the supervisor
        return render_template('errors/403.html'), 403

    sleForm = SLEForm()

    existing_final_evaluation = StudentLaborEvaluation.get_or_none(formHistoryID = laborHistoryForm, is_midyear_evaluation = False, is_submitted = True)
    existing_midyear_evaluation = StudentLaborEvaluation.get_or_none(formHistoryID = laborHistoryForm, is_midyear_evaluation = True, is_submitted = True)
    existing_saved_evaluation = StudentLaborEvaluation.select().where(StudentLaborEvaluation.formHistoryID == laborHistoryForm, StudentLaborEvaluation.is_submitted == False)
    if existing_saved_evaluation:
        existing_saved_evaluation = existing_saved_evaluation[-1]

    if not request.method == "POST":        # Doesn't override submitted POST data!
        if existing_midyear_evaluation:     # TODO Or there's savedforlater data
            sleForm.attendance.data = existing_midyear_evaluation.attendance_score
            sleForm.accountability.data = existing_midyear_evaluation.accountability_score
            sleForm.teamwork.data = existing_midyear_evaluation.teamwork_score
            sleForm.initiative.data = existing_midyear_evaluation.initiative_score
            sleForm.respect.data = existing_midyear_evaluation.respect_score
            sleForm.learning.data = existing_midyear_evaluation.learning_score
            sleForm.jobSpecific.data = existing_midyear_evaluation.jobSpecific_score

            sleForm.attendanceCommentsMidyear.data = "Midyear comments: \n" + existing_midyear_evaluation.attendance_comment
            sleForm.accountabilityCommentsMidyear.data = "Midyear comments: \n" + existing_midyear_evaluation.accountability_comment
            sleForm.teamworkCommentsMidyear.data = "Midyear comments: \n" + existing_midyear_evaluation.teamwork_comment
            sleForm.initiativeCommentsMidyear.data = "Midyear comments: \n" + existing_midyear_evaluation.initiative_comment
            sleForm.respectCommentsMidyear.data = "Midyear comments: \n" + existing_midyear_evaluation.respect_comment
            sleForm.learningCommentsMidyear.data = "Midyear comments: \n" + existing_midyear_evaluation.learning_comment
            sleForm.jobSpecificCommentsMidyear.data = "Midyear comments: \n" + existing_midyear_evaluation.jobSpecific_comment

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


    if not (laborHistoryForm.formID.termCode.isFinalEvaluationOpen or laborHistoryForm.formID.termCode.isMidyearEvaluationOpen) and not existing_final_evaluation and not existing_midyear_evaluation:
        return render_template('errors/403.html'), 403

    overall_score = 73      # The default value
    if existing_final_evaluation:
        overall_score = (existing_final_evaluation.attendance_score +
                        existing_final_evaluation.accountability_score +
                        existing_final_evaluation.teamwork_score +
                        existing_final_evaluation.initiative_score +
                        existing_final_evaluation.respect_score +
                        existing_final_evaluation.learning_score +
                        existing_final_evaluation.jobSpecific_score)
    elif existing_midyear_evaluation:
        overall_score = (existing_midyear_evaluation.attendance_score +
                        existing_midyear_evaluation.accountability_score +
                        existing_midyear_evaluation.teamwork_score +
                        existing_midyear_evaluation.initiative_score +
                        existing_midyear_evaluation.respect_score +
                        existing_midyear_evaluation.learning_score +
                        existing_midyear_evaluation.jobSpecific_score)

    if sleForm.validate_on_submit():
        # First delete any temporarily saved data (is_submitted = False)
        if laborHistoryForm.formID.termCode.isMidyearEvaluationOpen:
            try:
                StudentLaborEvaluation.get(formHistoryID = laborHistoryForm, is_submitted = False, is_midyear_evaluation = True).delete_instance()
            except DoesNotExist:
                pass
        else:
            try:
                StudentLaborEvaluation.get(formHistoryID = laborHistoryForm, is_submitted = False, is_midyear_evaluation = False).delete_instance()
            except DoesNotExist:
                pass

        # Then, save the new record
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
                                    is_submitted = True if sleForm.isSubmitted.data == "True" else False
                                )
        if laborHistoryForm.formID.termCode.isMidyearEvaluationOpen:
            studentLaborEvaluation.is_midyear_evaluation = True
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
                            existing_final_evaluation = existing_final_evaluation,
                            existing_midyear_evaluation = existing_midyear_evaluation,
                            overall_score = overall_score,
                            isFinalEvaluationOpen = laborHistoryForm.formID.termCode.isFinalEvaluationOpen
                          )
