from app.models import *
from app.models.laborStatusForm import LaborStatusForm
from datetime import datetime
from app.models.emailHandler import sendExpirationEmail

def expireStudentConfirmations():
    forms = (LaborStatusForm.select().where(
        LaborStatusForm.isExpired == True, 
        ))
    for form in forms:


expireStudentConfirmations()