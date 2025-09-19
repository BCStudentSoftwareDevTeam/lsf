import os
from datetime import date
from app import app as flask_app
from app.models.laborStatusForm import LaborStatusForm
from app.models.formHistory import FormHistory
from app.logic.emailHandler import emailHandler

BASE_URL = os.getenv("EXTERNAL_BASE_URL", "http://localhost:5000/")

def expireStudentConfirmations():
    # Pick all forms whose confirmation deadline is today or earlier
    expired_forms = (
        LaborStatusForm
        .select()
        .where(
            (LaborStatusForm.studentExpirationDate.is_null(False)) &
            (LaborStatusForm.studentExpirationDate <= date.today())
        )
    )
    for form in expired_forms:
        try:
            lsfID = form.laborStatusFormID
            # Use the latest FormHistory entry for this LSF
            latest_history = (
                FormHistory
                .select()
                .where(FormHistory.formID == form)
                .order_by(FormHistory.formHistoryID.desc())
                .first()
            )
            if not latest_history:
                print(f"[SKIP] No FormHistory for LSF#{lsfID}")
                continue

            fh_pk = latest_history.formHistoryID
            print(f"[LOOP] LSF#{lsfID} exp={form.studentExpirationDate} → FH#{fh_pk}")

            emailer = emailHandler(fh_pk)
            emailer.laborStatusFromExpired()

        except Exception as e:
            import traceback
            print(f"[ERROR] While processing LSF#{getattr(form, 'laborStatusFormID', None)}: {e}")
            traceback.print_exc()

def main():
    # Ensure Flask context and a request base_url so templates/links render correctly
    with flask_app.app_context():
        from flask import has_request_context
        if not has_request_context():
            from flask import request
        # Provide a fake request context so request.host_url exists in email templates
        with flask_app.test_request_context("/", base_url=BASE_URL):
            expireStudentConfirmations()

if __name__ == "__main__":
    main()
    print("Automated Form Expiration Script Executed")
