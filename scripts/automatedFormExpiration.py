from app.models import *
from app.models.laborStatusForm import LaborStatusForm
from datetime import datetime
from app.logic.emailHandler import emailHandler

def expireStudentConfirmations():
    forms = (LaborStatusForm.select().where(
        LaborStatusForm.studentExpirationDate != None, 
        ))
    for form in forms:
        if form.isExpired():
            # resend but only to students
            emailer = emailHandler(form.lsf.formID)
            emailer.laborStatusFromExpired(toStudent=False, toSupervisor=True, toDept=False)
def main():
    expireStudentConfirmations()

if __name__ == "__main__":
    main()
    print("Automated Form Expiration Script Executed") 