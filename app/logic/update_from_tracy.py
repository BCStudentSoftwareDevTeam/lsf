from datetime import *
from app.models.Tracy import db
from app.models.Tracy.studata import STUDATA
from app.models.Tracy.stuposn import STUPOSN
from app.models.Tracy.stustaff import STUSTAFF
from app.models.supervisor import Supervisor
from app.models.student import Student
from app.models.department import Department
from app.models.user import User
from app.models.term import Term
from app.models.laborStatusForm import LaborStatusForm
from app.models.formHistory import FormHistory
from app.models.notes import Notes
 
 
 
 
 
def update_user(bnum_search):

    studentRecord=STUDATA.query.order_by(STUDATA.ID).all()
    StaffRecord=STUSTAFF.query.order_by(STUSTAFF.ID).all()
    for record in studentRecord:
        Student.update(FIRST_NAME=record.FIRST_NAME,
                       LAST_NAME=record.LAST_NAME,
                       PIDM=record.PIDM,
                       CLASS_LEVEL=record.CLASS_LEVEL,
                       ACADEMIC_FOCUS=record.ACADEMIC_FOCUS,
                       MAJOR=record.MAJOR,
                       PROBATION=record.PROBATION,
                       ADVISOR=record.ADVISOR,
                       STU_EMAIL=record.STU_EMAIL,
                       STU_CPO=record.STU_CPO,
                       LAST_POSN=record.LAST_POSN,
                       LAST_SUP_PIDM=record.LAST_SUP_PIDM).where(Student.ID==record.ID).execute()
    # for record in StaffRecord:
    #     Student.update(FIRST_NAME=record.FIRST_NAME,
    #                 LAST_NAME=record.LAST_NAME,
    #                 PIDM=record.PIDM,
    #                 CLASS_LEVEL=record.CLASS_LEVEL,
    #                 ACADEMIC_FOCUS=record.ACADEMIC_FOCUS,
    #                 MAJOR=record.MAJOR,
    #                 PROBATION=record.PROBATION,
    #                 ADVISOR=record.ADVISOR,
    #                 STU_EMAIL=record.STU_EMAIL,
    #                 STU_CPO=record.STU_CPO,
    #                 LAST_POSN=record.LAST_POSN,
    #                 LAST_SUP_PIDM=record.LAST_SUP_PIDM).where(Student.ID==record.ID).execute()

    return(studentRecord)