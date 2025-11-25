import os
from datetime import date
from app import app as flask_app
from app.models.laborStatusForm import LaborStatusForm
from app.models.formHistory import FormHistory
from app.logic.emailHandler import emailHandler
from app.models.emailTracker import EmailTracker
from flask import request, has_request_context

#emailhistory requires an active flask app context so we create one to supplement it
def get_base_url():
    if has_request_context():
        # Build the full root URL (e.g., http://localhost:8080)
        return request.url_root.rstrip('/')
    else:
        # Fallback if there’s no request context 
        return os.getenv("EXTERNAL_BASE_URL", "http://localhost:5000")


def expireStudentConfirmations():
    expired_forms = (
        LaborStatusForm
        .select()
        .where(
            (LaborStatusForm.studentExpirationDate.is_null(False)) &
            (LaborStatusForm.studentExpirationDate <= date.today())
        )
    )
    print(f"Found {len(expired_forms)} expired forms")
    emailsSent = EmailTracker.select().count()
    for form in expired_forms:
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
        emailer.laborStatusFormExpired()
    sentEmailCount = EmailTracker.select().count() - emailsSent

    print(f"Sent {sentEmailCount} emails.") 


def main():
    with flask_app.app_context():
        if not has_request_context():
            with flask_app.test_request_context("/", base_url=get_base_url()):
                expireStudentConfirmations()

if __name__ == "__main__":
    main()
