'''Add new fields to this file and run it to add new enteries into your local database.
Chech phpmyadmin to see if your changes are reflected
This file will need to be changed if the format of models changes (new fields, dropping fields, renaming...)'''

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
from.app.models.StudentLaborEvaluation import StudentLaborEvaluation

print("Inserting data for demo and testing purposes")

#############################
# Students (TRACY)
#############################
bothStudents = [
                {
                "ID":"B00730361",
                "PIDM":"1",
                "FIRST_NAME":"Elaheh",
                "LAST_NAME":"Jamali",
                "CLASS_LEVEL":"Junior",
                "ACADEMIC_FOCUS":"Computer Science",
                "MAJOR":"Computer Science",
                "PROBATION":"0",
                "ADVISOR":"Jan Pearce",
                "STU_EMAIL":"jamalie@berea.edu",
                "STU_CPO":"718",
                "LAST_POSN":"Media Technician",
                "LAST_SUP_PIDM":"7"
                },
                {
                "ID":"B00734292",
                "PIDM":"3",
                "FIRST_NAME":"Guillermo",
                "LAST_NAME":"Adams", # Guillermo's last name is wrong on purpose
                "CLASS_LEVEL":"Junior",
                "ACADEMIC_FOCUS":"Computer Science",
                "MAJOR":"Computer Science",
                "PROBATION":"0",
                "ADVISOR":"Jan Pearce",
                "STU_EMAIL":"cruzg@berea.edu",
                "STU_CPO":"300",
                "LAST_POSN":"TA",
                "LAST_SUP_PIDM":"7"
                },
                ]
localStudents = [
                {
                "ID":"B00841417",
                "PIDM":"2",
                "FIRST_NAME":"Alex",
                "LAST_NAME":"Bryant",
                "CLASS_LEVEL":"Senior",
                "ACADEMIC_FOCUS":"Computer Science",
                "MAJOR":"Computer Science",
                "PROBATION":"0",
                "ADVISOR":"Scott Heggen",
                "STU_EMAIL":"bryantal@berea.edu",
                "STU_CPO":"212",
                "LAST_POSN":"Student Manager",
                "LAST_SUP_PIDM":"7"
                },
        ]
tracyStudents = [
                {
                "ID":"B00785329",
                "PIDM":"4",
                "FIRST_NAME":"Kat",
                "LAST_NAME":"Adams",
                "CLASS_LEVEL":"Senior",
                "ACADEMIC_FOCUS":"Computer Science",
                "MAJOR":"Computer Science",
                "PROBATION":"0",
                "ADVISOR":"Scott Heggen",
                "STU_EMAIL":"adamskg@berea.edu",
                "STU_CPO":"420",
                "LAST_POSN":"TA",
                "LAST_SUP_PIDM":"7"
                },
                {
                "ID":"            B00888329",
                "PIDM":"7",
                "FIRST_NAME":"Jeremiah",
                "LAST_NAME":"Bullfrog",
                "CLASS_LEVEL":"Senior",
                "ACADEMIC_FOCUS":"Computer Science",
                "MAJOR":"Computer Science",
                "PROBATION":"0",
                "ADVISOR":"Scott Heggen",
                "STU_EMAIL":"bullfrogj@berea.edu",
                "STU_CPO":"420",
                "LAST_POSN":"TA",
                "LAST_SUP_PIDM":"7"
                }
]

# Add students to Tracy db
for student in (tracyStudents + bothStudents):
    db.session.add(STUDATA(**student))
    db.session.commit()

# Add the Student records
students = []
for student in (localStudents + bothStudents):
    # Set up lsf db data
    del student["PIDM"]
    student['ID'] = student['ID'].strip()
    students.append(student)
Student.insert_many(students).on_conflict_replace().execute()
print(" * students (TRACY) added")

#############################
# Positions (TRACY)
#############################
positions = [
            {
            "POSN_CODE": "S61407",
            "POSN_TITLE": "Student Programmer",
            "WLS": "1",
            "ORG" : "2114",
            "ACCOUNT":"6740",
            "DEPT_NAME":"Computer Science"
            },
            {
            "POSN_CODE": "S61408",
            "POSN_TITLE": "Research Associate",
            "WLS": "5",
            "ORG" : "2114",
            "ACCOUNT":"6740",
            "DEPT_NAME":"Computer Science"
            },
            {
            "POSN_CODE": "S61419",
            "POSN_TITLE": "Teaching Associate",
            "WLS": "3",
            "ORG" : "2114",
            "ACCOUNT":"6740",
            "DEPT_NAME":"Computer Science"
            },
            {
            "POSN_CODE": "S61420",
            "POSN_TITLE": "Teaching Associate",
            "WLS": "5",
            "ORG" : "2147",
            "ACCOUNT":"6740",
            "DEPT_NAME":"Technology and Applied Design"
            },
            {
            "POSN_CODE": "S61421",
            "POSN_TITLE": "TA",
            "WLS": "6",
            "ORG" : "2114",
            "ACCOUNT":"6740",
            "DEPT_NAME":"Computer Science"
            },
            {
            "POSN_CODE": "S61427",
            "POSN_TITLE": "Teaching Associate",
            "WLS": "2",
            "ORG" : "2150",
            "ACCOUNT":"6740",
            "DEPT_NAME":"Mathematics"
            },
            {
            "POSN_CODE": "S61430",
            "POSN_TITLE": "Teaching Associate",
            "WLS": "5",
            "ORG" : "2107",
            "ACCOUNT":"6740",
            "DEPT_NAME":"Biology"
            },
            {
            "POSN_CODE": "S61443",
            "POSN_TITLE": "Lab Assistant",
            "WLS": "6",
            "ORG" : "2107",
            "ACCOUNT":"6740",
            "DEPT_NAME":"Biology"
            },
            {
            "POSN_CODE": "S12345",
            "POSN_TITLE": "DUMMY POSITION",
            "WLS": "3",
            "ORG" : "2114",
            "ACCOUNT":"6740",
            "DEPT_NAME":"Computer Science"
            }
]
# Add to Tracy db
for position in positions:
    db.session.add(STUPOSN(**position))
    db.session.commit()

print(" * positions (TRACY) added")

#############################
# TRACY Staff
#############################
staffs = [

            {
            "ID": "B12361006",
            "PIDM":1,
            "FIRST_NAME":"Scott",
            "LAST_NAME" : "Heggen",
            "EMAIL"  :"heggens@berea.edu",
            "CPO":"6300",
            "ORG":"2114",
            "DEPT_NAME": "Computer Science"
            },

            {
            "ID": "B12365892",
            "PIDM":2,
            "FIRST_NAME":"Jan",
            "LAST_NAME" : "Pearce",
            "EMAIL"  :"pearcej@berea.edu",
            "CPO":"6301",
            "ORG":"2114",
            "DEPT_NAME": "Computer Science"
            },
            {
            "ID": "B12365893",
            "PIDM":5,
            "FIRST_NAME":"Jasmine",
            "LAST_NAME" : "Jones",
            "EMAIL"  :"jonesj@berea.edu",
            "CPO":"6301",
            "ORG":"2114",
            "DEPT_NAME": "Computer Science"
            },
            {
            "ID": "B00763721",
            "PIDM":6,
            "FIRST_NAME":"Brian",
            "LAST_NAME" : "Ramsay",
            "EMAIL"  :"ramsayb2@berea.edu",
            "CPO":"6305",
            "ORG":"2114",
            "DEPT_NAME": "Computer Science"
            },
            {
            "ID": "B00841417",
            "PIDM":7,
            "FIRST_NAME":"Alex",
            "LAST_NAME" : "Bryant",
            "EMAIL"  :"bryantal@berea.edu",
            "CPO":"420",
            "ORG":"2114",
            "DEPT_NAME": "Computer Science"
            }
        ]

non_supervisor_staffs = [
                        {
                        "ID": "B1236237",
                        "PIDM":4,
                        "FIRST_NAME":"Megan",
                        "LAST_NAME" : "Hoffman",
                        "EMAIL"  :"hoffmanm@berea.edu",
                        "CPO":"6303",
                        "ORG":"2107",
                        "DEPT_NAME": "Biology"
                        },
                        {
                        "ID": "B1236236",
                        "PIDM":3,
                        "FIRST_NAME":"Mario",
                        "LAST_NAME" : "Nakazawa",
                        "EMAIL"  :"nakazawam@berea.edu",
                        "CPO":"6302",
                        "ORG":"2150",
                        "DEPT_NAME": "Mathematics"
                        }
                        ]

# Add to Tracy db
for staff in staffs:
    db.session.add(STUSTAFF(**staff))
    db.session.commit()

    Supervisor.get_or_create(**staff)

# Add non Supervisor staffs to Tracy db
for staff in non_supervisor_staffs:
    db.session.add(STUSTAFF(**staff))
    db.session.commit()

print(" * staff added")


#############################
# Users
#############################
users = [
        {
        "student": None,
        "supervisor": "B12361006",
        "username": "heggens",
        "isLaborAdmin": 1,
        "isFinancialAidAdmin": None,
        "isSaasAdmin": None
        },
        {
        "student": None,
        "supervisor": "B12365892",
        "username": "pearcej",
        "isLaborAdmin": None,
        "isFinancialAidAdmin": None,
        "isSaasAdmin": None
        },
        {
        "student": None,
        "supervisor": "B12365893",
        "username": "jonesj",
        "isLaborAdmin": None,
        "isFinancialAidAdmin": None,
        "isSaasAdmin": None
        },
        {
        "student": None,
        "supervisor": "B00763721",
        "username": "ramsayb2",
        "isLaborAdmin": 1,
        "isFinancialAidAdmin": None,
        "isSaasAdmin": None
        },
        {
        "student": "B00730361",
        "supervisor": None,
        "username": "jamalie",
        "isLaborAdmin": None,
        "isFinancialAidAdmin": None,
        "isSaasAdmin": None
        },
        {
        "student": "B00734292",
        "supervisor": None,
        "username": "cruzg",
        "isLaborAdmin": None,
        "isFinancialAidAdmin": None,
        "isSaasAdmin": None
        },
        {
        "student": "B00841417",
        "supervisor": "B00841417",
        "username": "bryantal",
        "isLaborAdmin": None,
        "isFinancialAidAdmin": None,
        "isSaasAdmin": None
        }
        ]
User.insert_many(users).on_conflict_replace().execute()
print(" * users added")



#############################
# Department
#############################
departments = [
            {
              "departmentID":1,
              "DEPT_NAME": "Computer Science",
              "ACCOUNT": "6740",
              "ORG": "2114",
              "departmentCompliance": 1
            },
            {
              "departmentID":2,
              "DEPT_NAME": "Technology and Applied Design",
              "ACCOUNT": "6740",
              "ORG": "2147",
              "departmentCompliance": 1
            },
            {
              "departmentID":3,
              "DEPT_NAME": "Mathematics",
              "ACCOUNT": "6740",
              "ORG": "2150",
              "departmentCompliance": 1
            },
            {
              "departmentID":4,
              "DEPT_NAME": "Biology",
              "ACCOUNT": "6740",
              "ORG": "2107",
              "departmentCompliance": 1
            },
        ]
Department.insert_many(departments).on_conflict_replace().execute()
print(" * departments added")

#############################
# Term
#############################
terms = [
            {
            "termCode":"202000",
            "termName": "AY 2020-2021",
            "termStart":"2020-08-01",
            "termEnd" : "2021-05-01",
            "termState": 1,
            "primaryCutOff": "2020-09-01",
            "adjustmentCutOff": "2020-09-01"
            },
            {
            "termCode":"202001",
            "termName": "Thanksgiving Break 2020",
            "termStart":"2020-08-01",
            "termEnd" : "2021-05-01",
            "termState": 0,
            "primaryCutOff": "2020-09-01",
            "adjustmentCutOff": "2020-09-01",
            "isBreak": 1
            }
       ]
Term.insert_many(terms).on_conflict_replace().execute()
print(" * terms added")

#############################
# Create a Pending Labor Status Form
#############################
LaborStatusForm.insert([{
            "laborStatusFormID": 2,
            "termCode_id": "202000",
            "studentName": "Alex Bryant",
            "studentSupervisee_id": "B00841417",
            "supervisor_id": "B12361006",
            "department_id": 1,
            "jobType": "Primary",
            "WLS": 1,
            "POSN_TITLE": "Student Programmer",
            "POSN_CODE": "S61407",
            "weeklyHours": 10,
            "startDate": "2020-04-01",
            "endDate": "2020-09-01"
        }]).on_conflict_replace().execute()
FormHistory.insert([{
            "formHistoryID": 2,
            "formID_id": "2",
            "historyType_id": "Labor Status Form",
            "createdBy_id": 1,
            "createdDate": "2020-04-14",
            "status_id": "Pending"
        }]).on_conflict_replace().execute()


#############################
# admin Notes
#############################
notes = [
            {
            "noteHistoryID": 1,
            "formID_id": 2,
            "date":"2020-01-01",
            "createdBy" : 1,
            "notesContents": "This is the first note",
            "noteType" : "Supervisor Note"
            },
            {
            "noteHistoryID": 2,
            "formID_id": 2,
            "date":"2020-02-01",
            "createdBy" : 1,
            "notesContents": "This is the second note",
            "noteType" : "Labor Note"
            },
       ]
Notes.insert_many(notes).on_conflict_replace().execute()
print(" * laborOfficeNotes added")

StudentLaborEvaluation  = [
                            { "ID": 1,
                              "formHistoryID": 1,


                            }


]


"""
Here is dummy data to test student labor evals:


AY 2021-2022,
Approved,
BXXXXXXXXX,
Student Name,
fakeStudent@berea.edu,
Primary,
S77111,
Residence Advisor,
3,15,,2022-01-17,2022-05-08,
Student Life - Hall Leadership,
Fake Supervisor,
supervisorName@berea.edu,
Start Date Correction,
Final,
20,
“Student has shown up on time for her duty nights. If she was running late or had to miss a meeting, etc. she would communicate this with the team.“,
9,
“This is their first semester, so she completed tasks as assigned, while trying to learning more about her responsibilities throughout the semester. Has followed policy while enforcing it, and has supported other policies and cared for workplace equipment, etc.“,
8,
“Works well with the rest of the team by communicating needs, and being willing to switch shifts if needed. Has collaborated with an event. Could grow with collaborating with other staff. “,
9,
“She takes initiative by asking questions about how to excel and improve in her role as Hall staff. She does need help, so she did need guidance, but once she knew what she needed to do - she did it well. They has been flexible, and was willing to make changes to her schedule as needed for the team.“,
10,
She has always demonstrated a willingness to learn and work well with her teammates.,
19,
“She as previously mentioned, takes initiative in reaching out to her supervisor and teammates about her role. She has shared knowledge in terms of letting the team know what is happening in the hall, (e.g. resident concerns). She has shared information with another new hall staff to help her grow, as well.
“,
18,
She has done well with her job overall. ,93

"""
