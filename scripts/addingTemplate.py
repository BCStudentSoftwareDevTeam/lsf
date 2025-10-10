import os
from datetime import date
from app import app as flask_app
from app.models.laborStatusForm import LaborStatusForm
from app.models.formHistory import FormHistory
from app.logic.emailHandler import emailHandler
from app.models.emailTemplate import*
from flask import has_request_context

emailTemplates = {
    # Email sent to admins when a labor release form is submitted
    "laborReleaseAdminNotification": {
        "purpose": "Labor Release Form Admin Notification",
        "formType": "Labor Status Form",
        "action": "Expired",
        "subject": "Student has been proposed to be released by their supervisor",
        "body": (
            "<p>Dear <strong>@@Admin@@</strong>,</p>"
            "<p>This email is to notify that the Labor Status Form submitted by "
            "<strong>@@Creator@@</strong> for <strong>@@Student@@</strong> has expired.</p>"
            "<p>&nbsp;</p>"
            "<p>You can resubmit the Labor Status Form for the <strong>@@Student@@</strong>.</p>"
            "<p>Sincerely,</p>"
            "<p>Labor Program Office</p>"
            "<p>labor_program@berea.edu</p>"
            "<p>859-985-3611</p>"
        ),
        "audience": "Supervisor",
    },
}

def checkForTemplates():
    for template in emailTemplates.values():
        if EmailTemplate.select().where(EmailTemplate.purpose == template["purpose"]).count() == 0:
            print(f"No email template found. Creating one.")
            EmailTemplate.create(
                purpose=template["purpose"], 
                formType=template["formType"],
                action=template["action"], 
                subject=template["subject"], 
                body=template["body"], 
                audience=template["audience"])
            print(f"Created email template.")

checkForTemplates()