'''Add new fields to this file and run it to add new enteries into your local database.
Chech phpmyadmin to see if your changes are reflected
This file will need to be changed if the format of models changes (new fields, dropping fields, renaming...)'''

from app import app

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
from app.models.supervisorDepartment import SupervisorDepartment
from app.models.allocation import Allocation
from app.models.positionHistory import PositionHistory
 
print("Inserting data for demo and testing purposes")

#############################
# Students (TRACY)
#############################
bothStudents = [
     {
                "ID":"B12345773",
                "PIDM":"57",
                "FIRST_NAME":"Test",
                "LAST_NAME":"Taker",
                "CLASS_LEVEL":"Sophmore",
                "ACADEMIC_FOCUS":"Computer Science",
                "MAJOR":"Computer Science",
                "PROBATION":"0",
                "ADVISOR":"Jan Pearce",
                "STU_EMAIL":"student@berea.edu",
                "STU_CPO":"700",
                "LAST_POSN":"Media Technician",
                "LAST_SUP_PIDM":"7"
                },

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
                {
                "ID":"B00791326",
                "PIDM":"9",
                "FIRST_NAME":"Oluwagbayi",
                "LAST_NAME":"Makinde",
                "CLASS_LEVEL":"Junior",
                "ACADEMIC_FOCUS":"Computer Science",
                "MAJOR":"Computer Science",
                "PROBATION":"0",
                "ADVISOR":"Jan Pearce",
                "STU_EMAIL":"makindeo@berea.edu",
                "STU_CPO":"883",
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
                "ID":"B00888329",
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
                },
                {
                "ID":"B00751360",
                "PIDM":"90",
                "FIRST_NAME":"Tyler",
                "LAST_NAME":"Parton",
                "CLASS_LEVEL":"Senior",
                "ACADEMIC_FOCUS":"Computer Science",
                "MAJOR":"Computer Science",
                "PROBATION":"0",
                "ADVISOR":"Scott Heggen",
                "STU_EMAIL":"partont@berea.edu",
                "STU_CPO":"420",
                "LAST_POSN":"TA",
                "LAST_SUP_PIDM":"7"
                }
]

# Add students to Tracy db
with app.app_context():
    for student in (tracyStudents + bothStudents):
        db.session.add(STUDATA(**student))
        db.session.commit()

# Add the Student records
students = []
for student in (localStudents + bothStudents):
    # Set up lsf db data
    del student["PIDM"]
    student['ID'] = student['ID'].strip()
    student['legal_name'] = student['FIRST_NAME'].strip()
    del student['FIRST_NAME']

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
            },
            {
            "POSN_CODE": "S61409",
            "POSN_TITLE": "Labor Workers",
            "WLS": "1",
            "ORG" : "4022",
            "ACCOUNT":"6740",
            "DEPT_NAME":"Labor Department"
            }

]
# Add to Tracy db
with app.app_context():
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
            "ID": "B00769499",
            "PIDM":28,
            "FIRST_NAME":"Madina",
            "LAST_NAME" : "Solijonova",
            "EMAIL"  :"solijonovam@berea.edu",
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
            },
            {
            "ID": "B00939230",
            "PIDM":99,
            "FIRST_NAME":"Wario",
            "LAST_NAME" : "Nakazawa",
            "EMAIL"  :"nakazawaw@berea.edu",
            "CPO":"666",
            "ORG":"2114",
            "DEPT_NAME": "Computer Science"
            },
            {
            "ID": "B00222888",
            "PIDM":97,
            "FIRST_NAME":"Test",
            "LAST_NAME" : "Professor",
            "EMAIL"  :"professort@berea.edu",
            "CPO":"500",
            "ORG":"2114",
            "DEPT_NAME": "Computer Science"
            },
            {
            "ID": "B00888222",
            "PIDM":98,
            "FIRST_NAME":"Demo",
            "LAST_NAME" : "Z",
            "EMAIL"  :"demoz@berea.edu",
            "CPO":"999",
            "ORG":"2114",
            "DEPT_NAME": "Computer Science"
            },
            {
            "ID": "B00123112",
            "PIDM":92,
            "FIRST_NAME":"Supervisor",
            "LAST_NAME" : "Test",
            "EMAIL"  :"tests@berea.edu",
            "CPO":"888",
            "ORG":"2114",
            "DEPT_NAME": "Computer Science"
            },
            {
            "ID": "B00012213",
            "PIDM":91,
            "FIRST_NAME":"Sib",
            "LAST_NAME" : "Ztest",
            "EMAIL"  :"ztests@berea.edu",
            "CPO":"222",
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
with app.app_context():
    for staff in staffs:
        db.session.add(STUSTAFF(**staff))
        db.session.commit()

        staff['legal_name'] = staff['FIRST_NAME'].strip()
        del staff['FIRST_NAME']
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
        "student": "B00791326",
        "supervisor": None,
        "username": "makindeo",
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
        },
        {
        "student": "B12345773",
        "supervisor": None,
        "username": "test1",
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
#############################
# Active Departments
#############################
departments = [
            {
              "departmentID":1,
              "DEPT_NAME": "Computer Science",
              "ACCOUNT": "6740",
              "ORG": "2114",
              "departmentCompliance": 1,
              "isActive": 1
            },
            {
              "departmentID":2,
              "DEPT_NAME": "Technology and Applied Design",
              "ACCOUNT": "6740",
              "ORG": "2147",
              "departmentCompliance": 1,
              "isActive": 1
            },
            {
              "departmentID":3,
              "DEPT_NAME": "Mathematics",
              "ACCOUNT": "6740",
              "ORG": "2150",
              "departmentCompliance": 1,
              "isActive": 1
            },
            {
              "departmentID":4,
              "DEPT_NAME": "Biology",
              "ACCOUNT": "6740",
              "ORG": "2107",
              "departmentCompliance": 1,
              "isActive": 1
            }, 
            {
              "departmentID":5,
              "DEPT_NAME": "Labor Department",
              "ACCOUNT": "6740",
              "ORG": "4022",
              "departmentCompliance": 1,
              "isActive": 1
            },
#############################
# Inactive Departments
#############################
            
            {
              "departmentID":6,
              "DEPT_NAME": "Agriculture and Natural Resources",
              "ACCOUNT": "6740",
              "ORG": "1441",
              "departmentCompliance": 1,
              "isActive": 0
            },
            {
              "departmentID":7,
              "DEPT_NAME": "Art and Art History",
              "ACCOUNT": "6740",
              "ORG": "2004",
              "departmentCompliance": 1,
              "isActive": 0
            },
            {
              "departmentID":8,
              "DEPT_NAME": "Asian Studies",
              "ACCOUNT": "6740",
              "ORG": "9801",
              "departmentCompliance": 1,
              "isActive": 0
            },
            {
              "departmentID":9,
              "DEPT_NAME": "Appalachian Studies",
              "ACCOUNT": "6740",
              "ORG": "8787",
              "departmentCompliance": 1,
              "isActive": 0
            }, 
            {
              "departmentID":10,
              "DEPT_NAME": "Music",
              "ACCOUNT": "6740",
              "ORG": "4805",
              "departmentCompliance": 1,
              "isActive": 0
            }
        ]
Department.insert_many(departments).on_conflict_replace().execute()
print(" * departments added")

#############################
# Term
#############################


print("Current year:", "termName")

terms = [
    {
        "termCode": f"202000",
        "termName": f"AY 2020-2021",
        "termStart": f"2020-08-01",
        "termEnd": f"2021-05-01",
        "termState": 0,
        "primaryCutOff": f"2020-09-01",
        "adjustmentCutOff": f"2020-10-01",
    },
    {
        "termCode": f"202500",
        "termName": f"AY 2025-2026",
        "termStart": f"2025-08-01",
        "termEnd": f"2026-05-01",
        "termState": 1,
        "primaryCutOff": f"2025-09-01",
        "adjustmentCutOff": f"2025-09-01",
    },
    {
        "termCode": f"202501",
        "termName": f"Thanksgiving Break 2025",
        "termStart": f"2025-08-01",
        "termEnd": f"2026-05-01",
        "termState": 0,
        "primaryCutOff": f"2025-09-01",
        "adjustmentCutOff": f"2025-09-01",
        "isBreak": 1,
    },
    {
        "termCode": f"202600",
        "termName": f"AY 2026-2027",
        "termStart": f"2026-08-01",
        "termEnd": f"2027-05-01",
        "termState": 0,
        "primaryCutOff": f"2026-09-01",
        "adjustmentCutOff": f"2026-09-01",
        "isBreak": 1,
    },
]

Term.insert_many(terms).on_conflict_replace().execute()
print(f" * terms for 2025-2026 added")

#############################
# Create a Pending Labor Status Form
#############################

LaborStatusForm.insert([{
            "laborStatusFormID": 2,
            "termCode_id": f"202000",
            "studentName": "Alex Bryant",
            "studentSupervisee_id": "B00841417",
            "supervisor_id": "B12361006",
            "department_id": 1,
            "jobType": "Primary",
            "WLS": 1,
            "POSN_TITLE": "Student Programmer",
            "POSN_CODE": "S61407",
            "weeklyHours": 10,
            "startDate": f"2020-04-01",
            "endDate": f"2020-09-01"
        }]).on_conflict_replace().execute()
FormHistory.insert([{
            "formHistoryID": 2,
            "formID_id": "2",
            "historyType_id": "Labor Status Form",
            "createdBy_id": 1,
            "createdDate": f"2025-04-14",
            "status_id": "Pending"
        }]).on_conflict_replace().execute()

LaborStatusForm.insert([{
            "laborStatusFormID": 3,
            "termCode_id": f"202500",
            "studentName": "Test Taker",
            "studentSupervisee_id": "B12345773",
            "supervisor_id": "B12361006",
            "department_id": 5,
            "jobType": "Primary",
            "WLS": 1,
            "POSN_TITLE": "Labor Workers",
            "POSN_CODE": "S61409",
            "weeklyHours": 10,
            "startDate": f"2025-04-01",
            "endDate": "2025-09-01"
        }]).on_conflict_replace().execute()  

FormHistory.insert([{
            "formHistoryID": 3,
            "formID_id": "3",
            "historyType_id": "Labor Status Form",
            "createdBy_id": 1,
            "createdDate": f"2025-04-14",
            "status_id": "Approved"
        }]).on_conflict_replace().execute()    


#############################
# Create Active Labor Status Form for the Break Term
#############################

# cs department

LaborStatusForm.insert([{
            "laborStatusFormID": 6,
            "termCode_id": f"202500",
            "studentName": "Pizza Taker",
            "studentSupervisee_id": "B12345773",
            "supervisor_id": "B12361006",
            "department_id": 1,
            "jobType": "Primary",
            "WLS": 1,
            "POSN_TITLE": "Media Technician",
            "POSN_CODE": "S61409",
            "contractHours": 15,
            "startDate": f"2025-04-01",
            "endDate": "2025-09-01"
        }]).on_conflict_replace().execute()  

FormHistory.insert([{
            "formHistoryID": 6,
            "formID_id": "6",
            "historyType_id": "Labor Status Form",
            "createdBy_id": 1,
            "createdDate": f"2025-04-14",
            "status_id": "Approved"
        }]).on_conflict_replace().execute()  

LaborStatusForm.insert([{
            "laborStatusFormID": 7,
            "termCode_id": f"202500",
            "studentName": "Elaheh Jamali",
            "studentSupervisee_id": "B00730361",
            "supervisor_id": "B12361006",
            "department_id": 1,
            "jobType": "Primary",
            "WLS": 1,
            "POSN_TITLE": "Media Technician",
            "POSN_CODE": "S61409",
            "contractHours": 3,
            "startDate": f"2025-04-01",
            "endDate": "2025-09-01"
        }]).on_conflict_replace().execute()  

FormHistory.insert([{
            "formHistoryID": 7,
            "formID_id": "7",
            "historyType_id": "Labor Status Form",
            "createdBy_id": 1,
            "createdDate": f"2025-04-14",
            "status_id": "Approved"
        }]).on_conflict_replace().execute()  



# labor department

LaborStatusForm.insert([{
            "laborStatusFormID": 4,
            "termCode_id": f"202500",
            "studentName": "Elaheh Jamali",
            "studentSupervisee_id": "B00730361",
            "supervisor_id": "B12361006",
            "department_id": 5,
            "jobType": "Secondary",
            "WLS": 1,
            "POSN_TITLE": "Media Technician",
            "POSN_CODE": "S61409",
            "contractHours": 5,
            "startDate": f"2025-04-01",
            "endDate": "2025-09-01"
        }]).on_conflict_replace().execute()  

FormHistory.insert([{
            "formHistoryID": 4,
            "formID_id": "4",
            "historyType_id": "Labor Status Form",
            "createdBy_id": 1,
            "createdDate": f"2025-04-14",
            "status_id": "Approved"
        }]).on_conflict_replace().execute()  

LaborStatusForm.insert([{
            "laborStatusFormID": 5,
            "termCode_id": f"202500",
            "studentName": "Elaheh Jamali",
            "studentSupervisee_id": "B00730361",
            "supervisor_id": "B12361006",
            "department_id": 5,
            "jobType": "Secondary",
            "WLS": 1,
            "POSN_TITLE": "Media Technician",
            "POSN_CODE": "S61409",
            "contractHours": 5,
            "startDate": f"2025-04-01",
            "endDate": "2025-09-01"
        }]).on_conflict_replace().execute()  

FormHistory.insert([{
            "formHistoryID": 5,
            "formID_id": "5",
            "historyType_id": "Labor Status Form",
            "createdBy_id": 1,
            "createdDate": f"2025-04-14",
            "status_id": "Approved"
        }]).on_conflict_replace().execute()  

# Biology Department

LaborStatusForm.insert([{
            "laborStatusFormID": 8,
            "termCode_id": f"202500",
            "studentName": "Elaheh Jamali",
            "studentSupervisee_id": "B00730361",
            "supervisor_id": "B12361006",
            "department_id": 4,
            "jobType": "Primary",
            "WLS": 1,
            "POSN_TITLE": "Media Technician",
            "POSN_CODE": "S61409",
            "contractHours": 5,
            "startDate": f"2025-04-01",
            "endDate": "2025-09-01"
        }]).on_conflict_replace().execute()  

FormHistory.insert([{
            "formHistoryID": 8,
            "formID_id": "8",
            "historyType_id": "Labor Status Form",
            "createdBy_id": 1,
            "createdDate": f"2025-04-14",
            "status_id": "Approved"
        }]).on_conflict_replace().execute()  

LaborStatusForm.insert([{
            "laborStatusFormID": 9,
            "termCode_id": f"202500",
            "studentName": "Elaheh Jamali",
            "studentSupervisee_id": "B00730361",
            "supervisor_id": "B12361006",
            "department_id": 4,
            "jobType": "Secondary",
            "WLS": 1,
            "POSN_TITLE": "Media Technician",
            "POSN_CODE": "S61409",
            "contractHours": 5,
            "startDate": f"2025-04-01",
            "endDate": "2025-09-01"
        }]).on_conflict_replace().execute()  

FormHistory.insert([{
            "formHistoryID": 9,
            "formID_id": "9",
            "historyType_id": "Labor Status Form",
            "createdBy_id": 1,
            "createdDate": f"2025-04-14",
            "status_id": "Approved"
        }]).on_conflict_replace().execute()

# Mathematics Department

LaborStatusForm.insert([{
            "laborStatusFormID": 10,
            "termCode_id": f"202500",
            "studentName": "Elaheh Jamali",
            "studentSupervisee_id": "B00730361",
            "supervisor_id": "B12361006",
            "department_id": 3,
            "jobType": "Primary",
            "WLS": 1,
            "POSN_TITLE": "Media Technician",
            "POSN_CODE": "S61409",
            "contractHours": 5,
            "startDate": f"2025-04-01",
            "endDate": "2025-09-01"
        }]).on_conflict_replace().execute()  

FormHistory.insert([{
            "formHistoryID": 10,
            "formID_id": "10",
            "historyType_id": "Labor Status Form",
            "createdBy_id": 1,
            "createdDate": f"2025-04-14",
            "status_id": "Approved"
        }]).on_conflict_replace().execute()  

LaborStatusForm.insert([{
            "laborStatusFormID": 11,
            "termCode_id": f"202500",
            "studentName": "Elaheh Jamali",
            "studentSupervisee_id": "B00730361",
            "supervisor_id": "B12361006",
            "department_id": 3,
            "jobType": "Secondary",
            "WLS": 1,
            "POSN_TITLE": "Media Technician",
            "POSN_CODE": "S61409",
            "contractHours": 5,
            "startDate": f"2025-04-01",
            "endDate": "2025-09-01"
        }]).on_conflict_replace().execute()  

FormHistory.insert([{
            "formHistoryID": 11,
            "formID_id": "11",
            "historyType_id": "Labor Status Form",
            "createdBy_id": 1,
            "createdDate": f"2025-04-14",
            "status_id": "Approved"
        }]).on_conflict_replace().execute()

#Technology and Applied Design Department

LaborStatusForm.insert([{
            "laborStatusFormID": 12,
            "termCode_id": f"202500",
            "studentName": "Elaheh Jamali",
            "studentSupervisee_id": "B00730361",
            "supervisor_id": "B12361006",
            "department_id": 2,
            "jobType": "Secondary",
            "WLS": 1,
            "POSN_TITLE": "Media Technician",
            "POSN_CODE": "S61409",
            "contractHours": 5,
            "startDate": f"2025-04-01",
            "endDate": "2025-09-01"
        }]).on_conflict_replace().execute()  

FormHistory.insert([{
            "formHistoryID": 12,
            "formID_id": "12",
            "historyType_id": "Labor Status Form",
            "createdBy_id": 1,
            "createdDate": f"2025-04-14",
            "status_id": "Approved"
        }]).on_conflict_replace().execute()  

LaborStatusForm.insert([{
            "laborStatusFormID": 13,
            "termCode_id": f"202500",
            "studentName": "Elaheh Jamali",
            "studentSupervisee_id": "B00730361",
            "supervisor_id": "B12361006",
            "department_id": 2,
            "jobType": "Primary",
            "WLS": 1,
            "POSN_TITLE": "Media Technician",
            "POSN_CODE": "S61409",
            "contractHours": 5,
            "startDate": f"2025-04-01",
            "endDate": "2025-09-01"
        }]).on_conflict_replace().execute()  

FormHistory.insert([{
            "formHistoryID": 13,
            "formID_id": "13",
            "historyType_id": "Labor Status Form",
            "createdBy_id": 1,
            "createdDate": f"2025-04-14",
            "status_id": "Approved"
        }]).on_conflict_replace().execute()

LaborStatusForm.insert([{
            "laborStatusFormID": 14,
            "termCode_id": f"202500",
            "studentName": "Elaheh Jamali",
            "studentSupervisee_id": "B00730361",
            "supervisor_id": "B12361006",
            "department_id": 2,
            "jobType": "Secondary",
            "WLS": 1,
            "POSN_TITLE": "Media Technician",
            "POSN_CODE": "S61409",
            "contractHours": 5,
            "startDate": f"2025-04-01",
            "endDate": "2025-09-01"
        }]).on_conflict_replace().execute()  

FormHistory.insert([{
            "formHistoryID": 14,
            "formID_id": "14",
            "historyType_id": "Labor Status Form",
            "createdBy_id": 1,
            "createdDate": f"2025-04-14",
            "status_id": "Approved"
        }]).on_conflict_replace().execute()  

LaborStatusForm.insert([{
            "laborStatusFormID": 15,
            "termCode_id": f"202500",
            "studentName": "Elaheh Jamali",
            "studentSupervisee_id": "B00730361",
            "supervisor_id": "B12361006",
            "department_id": 2,
            "jobType": "Primary",
            "WLS": 1,
            "POSN_TITLE": "Media Technician",
            "POSN_CODE": "S61409",
            "contractHours": 5,
            "startDate": f"2025-04-01",
            "endDate": "2025-09-01"
        }]).on_conflict_replace().execute()  

FormHistory.insert([{
            "formHistoryID": 15,
            "formID_id": "15",
            "historyType_id": "Labor Status Form",
            "createdBy_id": 1,
            "createdDate": f"2025-04-14",
            "status_id": "Approved"
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


##############################
# Departement Members 
##############################

supervisorDepartmentMembers = [
    {
        "supervisor": "B12361006",
        "department": 1,
        "isCoordinator": True
    }, 

    {
        "supervisor": "B12365892",
        "department": 1,
        "isCoordinator": False
    }, 

    {
        "supervisor": "B12365893",
        "department": 1,
        "isCoordinator": False
    }, 

    {
        "supervisor": "B00763721",
        "department": 1,
        "isCoordinator": False
    },

    {
        "supervisor": "B00841417",
        "department": 1,
        "isCoordinator": True
    },
    {
        "supervisor": "B00939230",
        "department": 1,
        "isCoordinator": False
    },
    {
        "supervisor": "B00888222",
        "department": 1,
        "isCoordinator": False
    },
    {
        "supervisor": "B00222888",
        "department": 1,
        "isCoordinator": False
    },
    {
        "supervisor": "B00123112",
        "department": 1,
        "isCoordinator": True
    },
    {
        "supervisor": "B00012213",
        "department": 1,
        "isCoordinator": True
    }
]

SupervisorDepartment.insert_many(supervisorDepartmentMembers).on_conflict_replace().execute()
print(" * Department members added")
print(f"termCode_id being used: {202500!r}")

############################
# Allocation Dummy Data:
###########################
allocations = [ 
    {
    "termCode":         202500,
    "department":       1,
    "isFinal":          True,
    "approvedOn":       None,
    "approvedBy":       None,
    "justification":    "We are hiring more students to help with the increased workload in the department",
    "primary_10":       5,
    "primary_12":       6,
    "primary_15":       4,
    "primary_20":       1,
    "secondary_5":      7,
    "secondary_10":     0,
    "breakHours":       550,
    },
    {
    "termCode":         202600,
    "department":       1,
    "isFinal":          False,
    "approvedOn":       None,
    "approvedBy":       None,
    "justification":    "We need even more students to help with the increased workload in the department",
    "primary_10":       8,
    "primary_12":       12,
    "primary_15":       5,
    "primary_20":       2,
    "secondary_5":      8,
    "secondary_10":     1,
    "breakHours":       560,
    },
    {
    "termCode":         202500,
    "department":       2,
    "isFinal":          True,
    "approvedOn":       None,
    "approvedBy":       None,
    "justification":    "Increase in student enrollment due to an exodus from the CS department",
    "primary_10":       4,
    "primary_12":       2,
    "primary_15":       7,
    "primary_20":       4,
    "secondary_5":      2,
    "secondary_10":     0,
    "breakHours":       750,
    },
    {
    "termCode":         202600,
    "department":       2,
    "isFinal":          False,
    "approvedOn":       None,
    "approvedBy":       None,
    "justification":    "We need more students than last year",
    "primary_10":       5,
    "primary_12":       3,
    "primary_15":       8,
    "primary_20":       5,
    "secondary_5":      3,
    "secondary_10":     0,
    "breakHours":       900,
    },
    {
    "termCode":         202500,
    "department":       3,
    "isFinal":          True,
    "approvedOn":       None,
    "approvedBy":       None,
    "justification":    "Downscaling due to decrease in student enrollment caused by current economic conditions",
    "primary_10":       2,
    "primary_12":       2,
    "primary_15":       1,
    "primary_20":       0,
    "secondary_5":      1,
    "secondary_10":     0,
    "breakHours":       260,
    },
    {
    "termCode":         202600,
    "department":       3,
    "isFinal":          False,
    "approvedOn":       None,
    "approvedBy":       None,
    "justification":    "Having more students, as economic conditions seem to improve",
    "primary_10":       5,
    "primary_12":       3,
    "primary_15":       3,
    "primary_20":       0,
    "secondary_5":      2,
    "secondary_10":     0,
    "breakHours":       360,
    },
    {
    "termCode":         202600,
    "department":       3,
    "isFinal":          True,
    "approvedOn":       None,
    "approvedBy":       None,
    "primary_10":       2,
    "primary_12":       2,
    "primary_15":       1,
    "primary_20":       0,
    "secondary_5":      1,
    "secondary_10":     0,
    "breakHours":       260,
    },
    {
    "termCode":         202500,
    "department":       4,
    "isFinal":          True,
    "approvedOn":       None,
    "approvedBy":       None,
    "justification":    "Downscaling the number of students in the department due to budget cuts",
    "primary_10":       4,
    "primary_12":       5,
    "primary_15":       0,
    "primary_20":       0,
    "secondary_5":      1,
    "secondary_10":     0,
    "breakHours":       300,
    },
    {
    "termCode":         202500,
    "department":       5,
    "isFinal":          True,
    "approvedOn":       None,
    "approvedBy":       None,
    "justification":    "Due to rapid department growth, we need to hire more students to help with the increased workload",
    "primary_10":       8,
    "primary_12":       10,
    "primary_15":       7,
    "primary_20":       4,
    "secondary_5":      5,
    "secondary_10":     1,
    "breakHours":       900,
    },
    {
    "termCode":         202600,
    "department":       5,
    "isFinal":          False,
    "approvedOn":       None,
    "approvedBy":       None,
    "justification":    "Due to rapid department growth, we need to hire even more students to help with the increased workload",
    "primary_10":       9,
    "primary_12":       11,
    "primary_15":       9,
    "primary_20":       12,
    "secondary_5":      3,
    "secondary_10":     9,
    "breakHours":       1200,
    }
    ]
Allocation.insert_many(allocations).on_conflict_replace().execute()

print(" * allocation added")


#############################
# Position History
#############################

positionHistory = [
    {
        "positionTitle": "Student Programmer",
        "positionCode": "S61407",
        "status": "Active",
        "wls": 1,
        "revisionDate": f"2025-07-01",
        "description": "",
        "department": 1
    },
    {
        
        "positionTitle": "Research Associate",
        "positionCode": "S61408",
        "status": "Active",
        "wls": 2,
        "revisionDate": f"2025-09-01",
        "revisionDate": f"2026-09-01",
        "description": "",
        "department": 1
    },
    {
        "positionTitle": "Labor Workers",
        "positionCode": "S61409",
        "status": "Active",
        "wls": 3,
        "revisionDate": f"2025-07-01",
        "description": "",
        "department": 1
    },
    {
        "positionTitle": "Teaching Associate",
        "positionCode": "S61411",
        "status": "Active",
        "wls":3,
        "revisionDate" : f"2026-01-01",
        "description": "",
        "department" : 1
    },
    {
        "positionTitle": "Teaching Associate",
        "positionCode": "S61410",
        "status": "Inactive",
        "wls":2,
        "revisionDate" : f"2026-01-01",
        "description": "",
        "department" : 3
    },
    {
        "positionTitle": "Teaching Associate",
        "positionCode": "S61410",
        "status": "Active",
        "wls":2,
        "revisionDate" : f"2026-03-29",
        "description": "",
        "department" : 3
    },
    {
        "positionTitle": "DUMMY POSITION",
        "positionCode": "S12345",
        "status": "Active",
        "wls":3,
        "revisionDate" : f"2026-01-23",
        "description": "",
        "department" : 1
    },
    {
        "positionTitle": "Junior Data Analyst",
        "positionCode": "S39568",
        "status": "Active",
        "wls":4,
        "revisionDate" : f"2026-01-31",
        "description": "",
        "department" : 1
    },
    {
        "positionTitle": "Student Manager",
        "positionCode": "S74933",
        "status": "Active",
        "wls":5,
        "revisionDate" : f"2026-04-01",
        "description": "",
        "department" : 1
    },
    {
        "positionTitle": "IT Technician",
        "positionCode": "S94932",
        "status": "Active",
        "wls":6,
        "revisionDate" : f"2026-05-03",
        "description": "",
        "department" : 1
    },
    {
        "positionTitle": "Human code generator",
        "positionCode": "S22222",
        "status": "Active",
        "wls":1,
        "revisionDate" : f"2026-05-03",
        "description": "",
        "department" : 1
    },
    {
        "positionTitle": "Senior Software Engineer",
        "positionCode": "S00000",
        "status": "Active",
        "wls":6,
        "revisionDate" : f"2026-05-03",
        "description": "",
        "department" : 1
    }
    
]
PositionHistory.insert_many(positionHistory).on_conflict_replace().execute()
print(" * position history added")