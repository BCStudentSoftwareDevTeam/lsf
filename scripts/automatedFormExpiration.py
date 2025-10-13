import os
from datetime import date
from app import app as flask_app
from app.models.laborStatusForm import LaborStatusForm
from app.models.formHistory import FormHistory
from app.logic.emailHandler import emailHandler
from app.models.emailTemplate import*
from flask import has_request_context

#emailhistory requires an active flask app context so we create one to supllement it
BASE_URL = os.getenv("EXTERNAL_BASE_URL", "http://localhost:5000/")

emailTemplates = {
    "supervisorTemplate":{
        "purpose":'Email when Labor Status Form is expired to Supervisor', 
        "formType":"Labor Status Form", 
        "action":"Expired", 
        "subject":'Labor Status Form Expired', 
        "body":'<p>Dear <strong>@@Supervisor@@</strong>,</p>   <p>This email is to notify that the Labor Status Form submitted by <strong>@@Creator@@</strong> for <strong>@@Student@@</strong> has expired.</p>   <p>&nbsp;</p>   <p>You can resubmit the Labor Status Form for the <strong>@@Student@@</strong>.</p>   <p>Sincerely,<br>Labor Program Office<br>labor_program@berea.edu<br>859-985-3611</p>', 
        "audience":"Supervisor",
    },
    "studentTemplate":{
        "purpose":'Email when Labor Status Form is expired to Student', 
        "formType":"Labor Status Form", 
        "action":"Expired", 
        "subject":'Labor Status Form Expired', 
        "body":'<p>Dear <strong>@@Student@@</strong>,</p>   <p>This email is to notify that the Labor Status Form submitted by <strong>@@Creator@@</strong> for you has expired.</p>   <p>&nbsp;</p>   <p>Please notify your supervisor <strong>@@Student@@</strong> to reubmit the form.</p>   <p>Sincerely,<br>Labor Program Office<br>labor_program@berea.edu<br>859-985-3611</p>', 
        "audience":"Student",
    }
}
         
def checkForTemplates():
    for template in emailTemplates.values():
        if EmailTemplate.select().where(EmailTemplate.purpose == template["purpose"]).count() == 0:
            EmailTemplate.create(
                purpose=template["purpose"], 
                formType=template["formType"],
                action=template["action"], 
                subject=template["subject"], 
                body=template["body"], 
                audience=template["audience"])
        
def expireStudentConfirmations():
    expired_forms = (
        LaborStatusForm
        .select()
        .where(
            (LaborStatusForm.studentExpirationDate.is_null(False)) &
            (LaborStatusForm.studentExpirationDate <= date.today())
        )
    )
    checkForTemplates()
    for form in expired_forms:
            lsfID = form.laborStatusFormID
            latest_history = (
                FormHistory
                .select()
                .where(FormHistory.formID == form)
                .order_by(FormHistory.formHistoryID.desc())
                .first()
            )
            if not latest_history:
                continue

            lsfHistory = latest_history.formHistoryID
            emailer = emailHandler(lsfHistory)
            emailer.laborStatusFromExpired()

        

def main():
    with flask_app.app_context():
        if not has_request_context():
            with flask_app.test_request_context("/", base_url=BASE_URL):
                expireStudentConfirmations()

if __name__ == "__main__":
    main()
