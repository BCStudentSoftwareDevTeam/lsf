from flask import Flask, request, render_template
from flask_mail import Mail, Message
from app.config.loadConfig import*
from app.models.emailTemplate import*
from app.models.laborReleaseForm import*
from app.models.laborStatusForm import*
from app.models.overloadForm import*
from app.models.formHistory import*
from app.models.supervisor import*
from app.models.user import*
from app.models.status import*
from datetime import datetime
from app.models.emailTracker import *
from app.logic.tracy import Tracy
import string
from app import app
import os
from datetime import datetime, date

class emailHandler():
    def __init__(self, formHistoryKey):
        secret_conf = get_secret_cfg()
        app.config.update(
            MAIL_SERVER=secret_conf['MAIL_SERVER'],
            MAIL_PORT=secret_conf['MAIL_PORT'],
            MAIL_USERNAME= secret_conf['MAIL_USERNAME'],
            MAIL_PASSWORD= secret_conf['MAIL_PASSWORD'],
            REPLY_TO_ADDRESS= secret_conf['REPLY_TO_ADDRESS'],
            MAIL_USE_TLS=secret_conf['MAIL_USE_TLS'],
            MAIL_USE_SSL=secret_conf['MAIL_USE_SSL'],
            MAIL_DEFAULT_SENDER=secret_conf['MAIL_DEFAULT_SENDER'],
            MAIL_OVERRIDE_ALL=secret_conf['MAIL_OVERRIDE_ALL'],
            ALWAYS_SEND_MAIL=secret_conf['ALWAYS_SEND_MAIL']
        )

        self.mail = Mail(app)

        self.formHistory = FormHistory.get(FormHistory.formHistoryID == formHistoryKey)
        self.laborStatusForm = self.formHistory.formID
        self.term = self.laborStatusForm.termCode
        self.student = self.laborStatusForm.studentSupervisee
        self.studentEmail = self.student.STU_EMAIL
        self.creatorEmail = self.formHistory.createdBy.supervisor.EMAIL
        self.supervisorEmail = self.laborStatusForm.supervisor.EMAIL
        self.date = self.laborStatusForm.startDate.strftime("%m/%d/%Y")
        self.weeklyHours = str(self.laborStatusForm.weeklyHours)
        self.contractHours = str(self.laborStatusForm.contractHours)

        self.positions = LaborStatusForm.select().where(LaborStatusForm.termCode == self.term, LaborStatusForm.studentSupervisee == self.student)
        self.supervisors = []
        for position in self.positions:
            self.supervisors.append(position.supervisor)

        if not self.term.isBreak:
            try:
                ayTermCode = str(self.laborStatusForm.termCode.termCode)[:-2] + '00'
                self.primaryEmail = None
                self.primaryForm = None
                self.primaryForm = FormHistory.select().join_from(FormHistory, LaborStatusForm) \
                                              .join_from(FormHistory, HistoryType).join_from(FormHistory, Status) \
                                              .where((FormHistory.formID.jobType == "Primary") &
                                                     (FormHistory.formID.studentSupervisee == self.laborStatusForm.studentSupervisee) &
                                                     ((FormHistory.formID.termCode == self.laborStatusForm.termCode) | (FormHistory.formID.termCode == ayTermCode)) &
                                                     (FormHistory.historyType.historyTypeName == "Labor Status Form") &
                                                     (FormHistory.status.statusName != "Denied")).get()
                self.primaryEmail = self.primaryForm.formID.supervisor.EMAIL
            except DoesNotExist:
                # This case happens from some of the old data
                pass

        self.link = ""
        self.releaseReason = ""
        self.releaseDate = ""
        self.newAdjustmentField = ""
        self.oldAdjustmentField = ""

        if self.formHistory.adjustedForm:
            if self.formHistory.adjustedForm.fieldAdjusted == "supervisor":
                from app.logic.userInsertFunctions import createSupervisorFromTracy
                newSupervisor = createSupervisorFromTracy(bnumber=self.formHistory.adjustedForm.newValue)
                self.newAdjustmentField = "Pending new Supervisor: {0} {1}".format(newSupervisor.FIRST_NAME, newSupervisor.LAST_NAME)
                self.oldAdjustmentField = "Current Supervisor: {0} {1}".format(self.formHistory.formID.supervisor.FIRST_NAME, self.formHistory.formID.supervisor.LAST_NAME)
            elif self.formHistory.adjustedForm.fieldAdjusted == "position":
                currentPosition = Tracy().getPositionFromCode(self.formHistory.adjustedForm.oldValue)
                newPosition = Tracy().getPositionFromCode(self.formHistory.adjustedForm.newValue)
                self.oldAdjustmentField = "Current Position: {0} ({1})".format(currentPosition.POSN_TITLE, currentPosition.WLS)
                self.newAdjustmentField = "Pending new Position: {0} ({1})".format(newPosition.POSN_TITLE, newPosition.WLS)
            else:
                self.oldAdjustmentField = "Current Hours: {0}".format(self.formHistory.adjustedForm.oldValue)
                self.newAdjustmentField = "Pending new Hours: {0}".format(self.formHistory.adjustedForm.newValue)

        try:
            self.releaseDate = self.formHistory.releaseForm.releaseDate.strftime("%m/%d/%Y")
            self.releaseReason = self.formHistory.releaseForm.reasonForRelease

        except Exception as e:
            # The error you should get when the form is not a release form
            # is the 'AttributeError' error. We expect to get the 'AttributeError',
            # but if we get anything else then we want to print the error
            if e.__class__.__name__ != "AttributeError":
                print (e)

    def send(self, message: Message):
        if app.config['ENV'] == 'production' or app.config['ALWAYS_SEND_MAIL']:

            # If we have set an override address
            if app.config['MAIL_OVERRIDE_ALL']:
                message.html = "<b>Original message intended for {}.</b><br>".format(", ".join(message.recipients)) + message.html
                message.recipients = [app.config['MAIL_OVERRIDE_ALL']]

            message.reply_to = app.config["REPLY_TO_ADDRESS"]
            self.mail.send(message)

        elif app.config['ENV'] == 'testing':
            # TODO: we really should have a way to check that we're sending emails that doesn't spam the logs
            pass
        else:
            print("ENV: {}. Email not sent to {}, subject '{}'.".format(app.config['ENV'], message.recipients, message.subject))



    # The methods of this class each handle a different email situation. Some of the methods need to handle
    # "primary" and "secondary" forms differently, but a majority do not need to differentiate between the two.
    # Every method will use the replaceText and sendEmail methods to accomplish the email sending.
    # The email templates are stored inside of the emailHandler model, and depending on which email template
    # is pulled from the model, and replaceText method will replace the neccesary keywords with the correct data.
    # The sendEmail method will handle all of the email sending once the email template has been populated.
    def laborStatusFormSubmitted(self):
        if self.laborStatusForm.jobType == 'Secondary':
            if self.term.isBreak:
                if len(list(self.positions)) > 1:
                    self.checkRecipient("Break Labor Status Form Submitted For Student",
                                        "Break Labor Status Form Submitted For Supervisor on Additional LSF")
                else:
                    self.checkRecipient("Break Labor Status Form Submitted For Student",
                                     "Break Labor Status Form Submitted For Supervisor")
            else:
                self.checkRecipient("Labor Status Form Submitted For Student",
                                    False,
                                    "Secondary Position Labor Status Form Submitted")
        else:
            self.checkRecipient("Labor Status Form Submitted For Student",
                          "Primary Position Labor Status Form Submitted")

    def laborStatusFormApproved(self):
        if self.laborStatusForm.jobType == 'Secondary':
            if self.term.isBreak:
                self.checkRecipient("Break Labor Status Form Approved For Student",
                                    "Break Labor Status Form Approved For Supervisor")
            else:
                self.checkRecipient("Labor Status Form Approved For Student",
                                    "Secondary Position Labor Status Form Approved")
        else:
            self.checkRecipient("Labor Status Form Approved For Student",
                          "Primary Position Labor Status Form Approved")

    def laborStatusFormRejected(self):
        if self.laborStatusForm.jobType  == 'Secondary':
            if self.term.isBreak:
                self.checkRecipient("Break Labor Status Form Rejected For Student",
                                    "Break Labor Status Form Rejected For Supervisor")
            else:
                self.checkRecipient("Labor Status Form Rejected For Student",
                                    "Secondary Position Labor Status Form Rejected")
        else:
            self.checkRecipient("Labor Status Form Rejected For Student",
                          "Primary Position Labor Status Form Rejected")

    def laborStatusFormAdjusted(self, newSupervisor=False):
        self.checkRecipient("Labor Status Form Adjusted For Student",
                      "Labor Status Form Adjusted For Supervisor")
        if newSupervisor:
            self.supervisorEmail = (Supervisor.get(Supervisor.ID == newSupervisor).EMAIL)
            self.checkRecipient(False,
                          "Labor Status Form Adjusted For Supervisor")

    def laborReleaseFormSubmitted(self):
        self.checkRecipient("Labor Release Form Submitted For Student",
                      "Labor Release Form Submitted For Supervisor")

    def laborReleaseFormApproved(self):
        self.checkRecipient("Labor Release Form Approved For Student",
                      "Labor Release Form Approved For Supervisor")


    def laborReleaseFormRejected(self):
        self.checkRecipient("Labor Release Form Rejected For Student",
                      "Labor Release Form Rejected For Supervisor")

    def LaborOverLoadFormSubmitted(self, link):
        """
        For the student email, the process will work as such:
        First, the student UI HTML shell will be populated with the neccesary data.
        Once populated, the HTML shell will be converted into a link. This link
        will then be used to replace the keyword "@@link@@" in the email template.
        Once this is finished, the email can then be sent.
        """
        self.link = link
        self.checkRecipient("Labor Overload Form Submitted For Student",
                      "Labor Overload Form Submitted For Supervisor")
    def laborOverloadFormStudentReminder(self,link):
        self.link = link
        self.checkRecipient("Labor Overload Form Submitted For Student")

    def LaborOverLoadFormSubmittedNotification(self):
        """
        Emails that will be sent after the student has submitted their
        reason for the overload form; One email will be just a confirmation
        email to the student and the other one will be for the labor office.
        """
        self.checkRecipient("Labor Overload Form Submitted Notification For Student",
                            "Labor Overload Form Submitted Notification For Labor Office")

    def LaborOverLoadFormApproved(self):
        self.checkRecipient("Labor Overload Form Approved For Student",
                      "Labor Overload Form Approved For Supervisor")

    def LaborOverLoadFormRejected(self):
        self.checkRecipient("Labor Overload Form Rejected For Student",
                            "Labor Overload Form Rejected For Supervisor")

    def notifyAdditionalLaborStatusFormSubmittedForBreak(self):
        # This is the submission
        self.checkRecipient(False, False, "Break Labor Status Form Submitted For Additional Supervisor")

    # Depending on the department specified, this method will send an email to either SASS or Financial Aid office
    # to notify them about the overload applocation they need to approve
    def overloadVerification(self, dept, link):
        """
        For the departments email, the process will work as such:
        First, the departments UI HTML shell will be populated with the neccesary data.
        Once populated, the HTML shell will be converted into a link. This link
        will then be used to replace the keyword "@@link@@" in the email template.
        Once this is finished, the email can then be sent.
        """
        # In order to keep track of when emails to 'SAAS' and 'Financial Aid'
        # are sent, the EmailTracker will create a new entry that points back to
        # the LSF form the email is being created for.
        secret_conf = get_secret_cfg()
        self.link = link
        emailList = []
        if dept == "SAAS":
            admins = User.select(User.username).where(User.isSaasAdmin == True)
            for admin in admins:
                emailList.append(admin.username + "@berea.edu")
        elif dept == "Financial Aid":
            emailList.append(secret_conf["financial_aid"]["email"])
        message = Message("Labor Overload Form Verification",
            recipients=emailList)
        emailTemplateID = EmailTemplate.get(EmailTemplate.purpose == "SAAS and Financial Aid Office")
        newEmailTracker = EmailTracker.create(
                        formID = self.laborStatusForm.laborStatusFormID,
                        date = datetime.today().strftime('%Y-%m-%d'),
                        recipient = dept,
                        subject = emailTemplateID.subject
                        )
        message.html = self.replaceText(emailTemplateID.body)

        self.send(message)

    # The function below was commented out becasuse there is no email template with the purpose "Labor Admin Notification"
    # Since an admin can still see the decision from SAAS or Financial Aid in the pending Overload Form Modal,
    # this function didn't seem neccesary but if we want to implement it, we just need to create a email template with that purpose
    # and uncomment lines 116 and 117 in financialAidOverload.py

    # def verifiedOverloadNotification(self):
    #     """ This email will be sent to Labor Admin when SAAS or Financial Aid Make
    #     a decision on an overload form"""
    #     message = Message("Verified Labor Overload Form Notification",
    #                 recipients=[""]) # TODO: Labor Admin email
    #     emailTemplateID = EmailTemplate.get(EmailTemplate.purpose == "Labor Admin Notification")
    #     newEmailTracker = EmailTracker.create(
    #                     formID = self.laborStatusForm.laborStatusFormID,
    #                     date = datetime.today().strftime('%Y-%m-%d'),
    #                     recipient = 'Labor Office',
    #                     subject = emailTemplateID.subject
    #                     )
    #     message.html = self.replaceText(emailTemplateID.body)
    #
    #     self.send(message)

    def checkRecipient(self, studentEmailPurpose=False, emailPurpose=False, secondaryEmailPurpose=False):
        """
        This method will take in two to three inputs of email purposes. An email to the student is always sent.
        The method then checks whether to send the email to only the primary or both the primary and secondary supervisors.
        The method sendEmail is then called to handle the actual sending of the emails.
        """
        if studentEmailPurpose:
            studentEmail = EmailTemplate.get(EmailTemplate.purpose == studentEmailPurpose)
            self.sendEmail(studentEmail, "student")
        if emailPurpose or secondaryEmailPurpose:
            if self.laborStatusForm.jobType == 'Secondary':
                if secondaryEmailPurpose:
                    secondaryEmail = EmailTemplate.get(EmailTemplate.purpose == secondaryEmailPurpose)
                    self.sendEmail(secondaryEmail, "secondary")
                else:
                    primaryEmail = EmailTemplate.get(EmailTemplate.purpose == emailPurpose)
                    self.sendEmail(primaryEmail, "supervisor")
            else:
                primaryEmail = EmailTemplate.get(EmailTemplate.purpose == emailPurpose)
                if primaryEmail.audience == "Labor Office":
                    self.sendEmail(primaryEmail, "Labor Office")
                else:
                    self.sendEmail(primaryEmail, "supervisor")

    # Depending on the parameter 'sendTo', this method will send the email either to the Primary, Secondary, or the Student
    def sendEmail(self, template, sendTo):
        formTemplate = template.body
        formTemplate = self.replaceText(formTemplate)
        if sendTo == "student":
            message = Message(template.subject,
                recipients=[self.studentEmail])
            recipient = 'Student'
        elif sendTo == "secondary":
            if self.term.isBreak:
                supervisorEmails = []
                for supervisor in self.supervisors:
                    supervisorEmails.append(supervisor.EMAIL)
                supervisorEmails = supervisorEmails[:-1]
                message = Message(template.subject,
                    recipients=supervisorEmails)
                recipient = 'Secondary Supervisor'
            else:
                message = Message(template.subject,
                    recipients=[self.supervisorEmail, self.primaryEmail])
                recipient = 'Primary Supervisor'
        elif sendTo == "Labor Office":
            message = Message(template.subject,
                recipients=[""]) #TODO: Email for the Labor Office
            recipient = 'Labor Office'
        elif sendTo == 'supervisor':
            message = Message(template.subject,
                recipients=[self.supervisorEmail])
            recipient = 'Primary Supervisor'
        message.html = formTemplate

        newEmailTracker = EmailTracker.create(
                        formID = self.laborStatusForm.laborStatusFormID,
                        date = datetime.today().strftime('%Y-%m-%d'),
                        recipient = recipient,
                        subject = template.subject
                        )

        self.send(message)

    # This method is responsible for replacing the keyword form the templates in the database with the data in the laborStatusForm
    def replaceText(self, form):
        form = form.replace("@@Creator@@", self.formHistory.createdBy.supervisor.FIRST_NAME + " " + self.formHistory.createdBy.supervisor.LAST_NAME)
        # 'Supervisor' is the supervisor on the current laborStatusForm that correspond to the formID we passed in when creating the class
        form = form.replace("@@Supervisor@@", self.laborStatusForm.supervisor.FIRST_NAME + " " + self.laborStatusForm.supervisor.LAST_NAME)
        form = form.replace("@@Student@@", self.laborStatusForm.studentSupervisee.FIRST_NAME + " " + self.laborStatusForm.studentSupervisee.LAST_NAME)
        form = form.replace("@@StudB@@", self.laborStatusForm.studentSupervisee.ID)
        form = form.replace("@@Position@@", self.laborStatusForm.POSN_CODE+ ", " + self.laborStatusForm.POSN_TITLE)
        form = form.replace("@@Department@@", self.laborStatusForm.department.DEPT_NAME)
        form = form.replace("@@WLS@@", self.laborStatusForm.WLS)
        form = form.replace("@@Term@@", self.term.termName)

        if self.formHistory.rejectReason:
            form = form.replace("@@RejectReason@@", self.formHistory.rejectReason)
        if self.laborStatusForm.weeklyHours != None:
            form = form.replace("@@Hours@@", self.weeklyHours)
        else:
            form = form.replace("@@Hours@@", self.contractHours)
        if self.term.isBreak:
            previousSupervisorNames = ""
            for supervisor in self.supervisors[:-1]:
                previousSupervisorNames += supervisor.FIRST_NAME + " " + supervisor.LAST_NAME + ", "
            previousSupervisorNames = previousSupervisorNames[:-2]
            form = form.replace("@@PreviousSupervisor(s)@@", previousSupervisorNames)
        elif self.primaryForm:
            # 'Primary Supervisor' is the primary supervisor of the student who's laborStatusForm is passed in the initializer
            form = form.replace("@@PrimarySupervisor@@", self.primaryForm.formID.supervisor.FIRST_NAME + " " + self.primaryForm.formID.supervisor.LAST_NAME)
        if self.formHistory.adjustedForm:
            form = form.replace("@@NewAdjustmentField@@", self.newAdjustmentField)
            form = form.replace("@@CurrentAdjustmentField@@", self.oldAdjustmentField)
        form = form.replace("@@SupervisorEmail@@", self.supervisorEmail)
        form = form.replace("@@Date@@", self.date)
        form = form.replace("@@ReleaseReason@@", self.releaseReason)
        form = form.replace("@@ReleaseDate@@", self.releaseDate)
        form = form.replace("@@link@@", self.link)
        return(form)
