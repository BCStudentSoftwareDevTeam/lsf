from app.models import *
from app.models.laborStatusForm import LaborStatusForm
from datetime import datetime
from app.logic.emailHandler import emailHandler
from app.models.emailTemplate import*

def expireStudentConfirmations():
    forms = (LaborStatusForm.select().where(
        LaborStatusForm.studentExpirationDate.is_null(False), 
        ))
    for form in forms:
        if form.isExpired:
            print(f"Expiring form ID: {form.get_id()} ")
            emailer = emailHandler(form.get_id())
            emailer.laborStatusFromExpired()
def main():
    expireStudentConfirmations()

if __name__ == "__main__":
    main()
    print("Automated Form Expiration Script Executed") 