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
from app.models.positionDescriptionSection import PositionDescriptionSection
 
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
                "ID":"B00741361",
                "PIDM":"99",
                "FIRST_NAME":"Antonia",
                "LAST_NAME":"Schmith",
                "CLASS_LEVEL":"Freshman",
                "ACADEMIC_FOCUS":"Computer Science",
                "MAJOR":"Computer Science",
                "PROBATION":"0",
                "ADVISOR":"Scott Heggen",
                "STU_EMAIL":"schmitha@berea.edu",
                "STU_CPO":"777",
                "LAST_POSN":"TA",
                "LAST_SUP_PIDM":"7"
                },
                {
                "ID":"B00732363",
                "PIDM":"58",
                "FIRST_NAME":"Barbara",
                "LAST_NAME":"Williams",
                "CLASS_LEVEL":"Junior",
                "ACADEMIC_FOCUS":"Computer Science",
                "MAJOR":"Computer Science",
                "PROBATION":"0",
                "ADVISOR":"Jasmine Jones",
                "STU_EMAIL":"williamsb@berea.edu",
                "STU_CPO":"118",
                "LAST_POSN":"TA",
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
                {"ID": "B00811617", "legal_name": "Chris Georgiev", "isActive": True, "PIDM": "8", "FIRST_NAME": "Chris", "LAST_NAME": "Georgiev"},
                {"ID": "B00815474", "legal_name": "Julius Fritz", "isActive": True, "PIDM": "9", "FIRST_NAME": "Julius", "LAST_NAME": "Fritz"},
                {"ID": "B12345223", "legal_name": "Subaru Natsuki", "isActive": True, "PIDM": "10", "FIRST_NAME": "Subaru", "LAST_NAME": "Natsuki"},
                {"ID": "B12345003", "legal_name": "Hatsune Miku", "isActive": True, "PIDM": "11", "FIRST_NAME": "Hatsune", "LAST_NAME": "Miku"},
                {"ID": "B12345772", "legal_name": "Michael Jackson", "isActive": True, "PIDM": "12", "FIRST_NAME": "Michael", "LAST_NAME": "Jackson"},
                {"ID": "B12345756", "legal_name": "Genji Overwatch", "isActive": True, "PIDM": "13", "FIRST_NAME": "Genji", "LAST_NAME": "Overwatch"},
                {"ID": "B12345759", "legal_name": "Mister Marlowe", "isActive": True, "PIDM": "14", "FIRST_NAME": "Mister", "LAST_NAME": "Marlowe"},
                {"ID": "B11231123", "legal_name": "Mister Thanksgiving", "isActive": True, "PIDM": "15", "FIRST_NAME": "Mister", "LAST_NAME": "Thanksgiving"},
                {"ID": "B12345762", "legal_name": "Alex Carter",      "isActive": True, "PIDM": "16", "FIRST_NAME": "Alex",   "LAST_NAME": "Carter"},
                {"ID": "B12345763", "legal_name": "Morgan Hayes",     "isActive": True, "PIDM": "17", "FIRST_NAME": "Morgan", "LAST_NAME": "Hayes"},
                {"ID": "B12345764", "legal_name": "Jordan Brooks",    "isActive": True, "PIDM": "18", "FIRST_NAME": "Jordan", "LAST_NAME": "Brooks"},
                {"ID": "B12345765", "legal_name": "Taylor Morgan",    "isActive": True, "PIDM": "19", "FIRST_NAME": "Taylor", "LAST_NAME": "Morgan"},
                {"ID": "B12345766", "legal_name": "Casey Turner",     "isActive": True, "PIDM": "20", "FIRST_NAME": "Casey",  "LAST_NAME": "Turner"},
                {"ID": "B12345767", "legal_name": "Jamie Foster",     "isActive": True, "PIDM": "21", "FIRST_NAME": "Jamie",  "LAST_NAME": "Foster"},
                {"ID": "B12345768", "legal_name": "Riley Cooper",     "isActive": True, "PIDM": "22", "FIRST_NAME": "Riley",  "LAST_NAME": "Cooper"},
                {"ID": "B12345769", "legal_name": "Drew Bennett",     "isActive": True, "PIDM": "23", "FIRST_NAME": "Drew",   "LAST_NAME": "Bennett"},
                {"ID": "B12345770", "legal_name": "Logan Price",      "isActive": True, "PIDM": "24", "FIRST_NAME": "Logan",  "LAST_NAME": "Price"},
                {"ID": "B12345771", "legal_name": "Avery Sullivan",   "isActive": True, "PIDM": "25", "FIRST_NAME": "Avery",  "LAST_NAME": "Sullivan"},

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
            {
              "departmentID":5,
              "DEPT_NAME": "Labor Department",
              "ACCOUNT": "6740",
              "ORG": "4022",
              "departmentCompliance": 1,
              "isActive": 1
            }

        ]
Department.insert_many(departments).on_conflict_replace().execute()
print(" * departments added")

#############################
# Term
#############################


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
        "termCode": "202600",
        "termName": "AY 2026-2027",
        "termStart": "2026-08-01",
        "termEnd": "2027-05-01",
        "termState": 0,
        "primaryCutOff": "2026-09-01",
        "adjustmentCutOff": "2026-10-01",
    },
    {
        "termCode": "202601",
        "termName": "Thanksgiving Break 2026",
        "termStart": "2026-08-01",
        "termEnd": "2027-05-01",
        "termState": 0,
        "primaryCutOff": "2026-09-01",
        "adjustmentCutOff": "2026-10-01",
        "isBreak": 1,
    },
    {
        "termCode": "202602",
        "termName": "Christmas Break 2026",
        "termStart": "2026-08-01",
        "termEnd": "2027-05-01",
        "termState": 0,
        "primaryCutOff": "2026-09-01",
        "adjustmentCutOff": "2026-10-01",
        "isBreak": 1,
    },
    {
        "termCode": "202603",
        "termName": "Spring Break 2027",
        "termStart": "2026-08-01",
        "termEnd": "2027-05-01",
        "termState": 0,
        "primaryCutOff": "2026-09-01",
        "adjustmentCutOff": "2026-10-01",
        "isBreak": 1,
    },
    {
        "termCode": "202604",
        "termName": "Fall Break 2026",
        "termStart": "2026-08-01",
        "termEnd": "2027-05-01",
        "termState": 0,
        "primaryCutOff": "2026-09-01",
        "adjustmentCutOff": "2026-10-01",
        "isBreak": 1,
    },
    {
        "termCode": "202611",
        "termName": "Fall 2026",
        "termStart": "2026-08-01",
        "termEnd": "2026-12-31",
        "termState": 0,
        "primaryCutOff": "2026-09-01",
        "adjustmentCutOff": "2026-10-01",
    },
    {
        "termCode": "202612",
        "termName": "Spring 2027",
        "termStart": "2027-01-01",
        "termEnd": "2027-05-01",
        "termState": 0,
        "primaryCutOff": "2027-02-01",
        "adjustmentCutOff": "2027-03-01",
    },
    {
        "termCode": "202613",
        "termName": "Summer 2027",
        "termStart": "2027-05-02",
        "termEnd": "2027-08-01",
        "termState": 0,
        "primaryCutOff": "2027-06-01",
        "adjustmentCutOff": "2027-07-01",
        "isSummer": 1,
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
LaborStatusForm.insert([{
    
            "laborStatusFormID": 9,
            "termCode_id": f"202500",
            "studentName": "Genji Overwatch",
            "studentSupervisee_id": "B12345756",
            "supervisor_id": "B12361006",
            "department_id": 1,
            "jobType": "Primary",
            "WLS": 1,
            "POSN_TITLE": "overwtahc guy",
            "POSN_CODE": "S61410",
            "contractHours": 15,
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
LaborStatusForm.insert([{

            "laborStatusFormID": 60,
            "termCode_id": f"202500",
            "studentName": "Mister Marlowe",
            "studentSupervisee_id": "B12345759",
            "supervisor_id": "B12361006",
            "department_id": 1,
            "jobType": "Primary",
            "WLS": 1,
            "POSN_TITLE": "Break Worker",
            "POSN_CODE": "S61412",
            "contractHours": 400,
            "startDate": f"2025-04-01",
            "endDate": "2025-09-01"

        }]).on_conflict_replace().execute()
FormHistory.insert([{
            "formHistoryID": 60,
            "formID_id": "60",
            "historyType_id": "Labor Status Form",
            "createdBy_id": 1,
            "createdDate": f"2025-04-14",
            "status_id": "Approved"
        }]).on_conflict_replace().execute()  
LaborStatusForm.insert([{

            "laborStatusFormID": 61,
            "termCode_id": f"202501",
            "studentName": "Mister Thanksgiving",
            "studentSupervisee_id": "B11231123",
            "supervisor_id": "B12361006",
            "department_id": 1,
            "jobType": "Primary",
            "WLS": 1,
            "POSN_TITLE": "Thanksgiving Worker",
            "POSN_CODE": "S61412",
            "contractHours": 50,
            "startDate": f"2025-11-23",
            "endDate": "2025-12-01"

        }]).on_conflict_replace().execute()
FormHistory.insert([{
            "formHistoryID": 61,
            "formID_id": "61",
            "historyType_id": "Labor Status Form",
            "createdBy_id": 1,
            "createdDate": f"2025-11-01",
            "status_id": "Approved"
        }]).on_conflict_replace().execute()   

LaborStatusForm.insert([{
    "laborStatusFormID": 62,
    "termCode_id": "202611",
    "studentName": "Alex Carter",
    "studentSupervisee_id": "B12345762",
    "supervisor_id": "B12361006",
    "department_id": 1,
    "jobType": "Primary",
    "WLS": 1,
    "POSN_TITLE": "Office Assistant",
    "POSN_CODE": "S61413",
    "weeklyHours": 10,
    "startDate": "2026-08-15",
    "endDate": "2026-12-15"
}]).on_conflict_replace().execute()

FormHistory.insert([{
    "formHistoryID": 62,
    "formID_id": "62",
    "historyType_id": "Labor Status Form",
    "createdBy_id": 1,
    "createdDate": "2026-08-01",
    "status_id": "Approved"
}]).on_conflict_replace().execute()


LaborStatusForm.insert([{
    "laborStatusFormID": 63,
    "termCode_id": "202611",
    "studentName": "Morgan Hayes",
    "studentSupervisee_id": "B12345763",
    "supervisor_id": "B12361006",
    "department_id": 1,
    "jobType": "Primary",
    "WLS": 1,
    "POSN_TITLE": "Computer Lab Assistant",
    "POSN_CODE": "S61414",
    "weeklyHours": 15,
    "startDate": "2026-08-15",
    "endDate": "2026-12-15"
}]).on_conflict_replace().execute()

FormHistory.insert([{
    "formHistoryID": 63,
    "formID_id": "63",
    "historyType_id": "Labor Status Form",
    "createdBy_id": 1,
    "createdDate": "2026-08-01",
    "status_id": "Approved"
}]).on_conflict_replace().execute()


LaborStatusForm.insert([{
    "laborStatusFormID": 64,
    "termCode_id": "202611",
    "studentName": "Jordan Brooks",
    "studentSupervisee_id": "B12345764",
    "supervisor_id": "B12361006",
    "department_id": 1,
    "jobType": "Primary",
    "WLS": 1,
    "POSN_TITLE": "Help Desk Assistant",
    "POSN_CODE": "S61415",
    "weeklyHours": 20,
    "startDate": "2026-08-15",
    "endDate": "2026-12-15"
}]).on_conflict_replace().execute()

FormHistory.insert([{
    "formHistoryID": 64,
    "formID_id": "64",
    "historyType_id": "Labor Status Form",
    "createdBy_id": 1,
    "createdDate": "2026-08-01",
    "status_id": "Approved"
}]).on_conflict_replace().execute()


LaborStatusForm.insert([{
    "laborStatusFormID": 65,
    "termCode_id": "202611",
    "studentName": "Taylor Morgan",
    "studentSupervisee_id": "B12345765",
    "supervisor_id": "B12361006",
    "department_id": 1,
    "jobType": "Secondary",
    "WLS": 0,
    "POSN_TITLE": "Reception Assistant",
    "POSN_CODE": "S61416",
    "weeklyHours": 5,
    "startDate": "2026-08-15",
    "endDate": "2026-12-15"
}]).on_conflict_replace().execute()

FormHistory.insert([{
    "formHistoryID": 65,
    "formID_id": "65",
    "historyType_id": "Labor Status Form",
    "createdBy_id": 1,
    "createdDate": "2026-08-01",
    "status_id": "Approved"
}]).on_conflict_replace().execute()


LaborStatusForm.insert([{
    "laborStatusFormID": 66,
    "termCode_id": "202611",
    "studentName": "Casey Turner",
    "studentSupervisee_id": "B12345766",
    "supervisor_id": "B12361006",
    "department_id": 1,
    "jobType": "Secondary",
    "WLS": 0,
    "POSN_TITLE": "Library Assistant",
    "POSN_CODE": "S61417",
    "weeklyHours": 10,
    "startDate": "2026-08-15",
    "endDate": "2026-12-15"
}]).on_conflict_replace().execute()

FormHistory.insert([{
    "formHistoryID": 66,
    "formID_id": "66",
    "historyType_id": "Labor Status Form",
    "createdBy_id": 1,
    "createdDate": "2026-08-01",
    "status_id": "Approved"
}]).on_conflict_replace().execute()

LaborStatusForm.insert([{
    "laborStatusFormID": 72,
    "termCode_id": "202612",
    "studentName": "Alex Carter",
    "studentSupervisee_id": "B12345762",
    "supervisor_id": "B12361006",
    "department_id": 1,
    "jobType": "Primary",
    "WLS": 1,
    "POSN_TITLE": "Office Assistant",
    "POSN_CODE": "S61413",
    "weeklyHours": 10,
    "startDate": "2027-01-15",
    "endDate": "2027-05-15"
}]).on_conflict_replace().execute()

FormHistory.insert([{
    "formHistoryID": 72,
    "formID_id": "72",
    "historyType_id": "Labor Status Form",
    "createdBy_id": 1,
    "createdDate": "2027-01-05",
    "status_id": "Approved"
}]).on_conflict_replace().execute()


LaborStatusForm.insert([{
    "laborStatusFormID": 73,
    "termCode_id": "202612",
    "studentName": "Morgan Hayes",
    "studentSupervisee_id": "B12345763",
    "supervisor_id": "B12361006",
    "department_id": 1,
    "jobType": "Primary",
    "WLS": 1,
    "POSN_TITLE": "Computer Lab Assistant",
    "POSN_CODE": "S61414",
    "weeklyHours": 15,
    "startDate": "2027-01-15",
    "endDate": "2027-05-15"
}]).on_conflict_replace().execute()

FormHistory.insert([{
    "formHistoryID": 73,
    "formID_id": "73",
    "historyType_id": "Labor Status Form",
    "createdBy_id": 1,
    "createdDate": "2027-01-05",
    "status_id": "Approved"
}]).on_conflict_replace().execute()


LaborStatusForm.insert([{
    "laborStatusFormID": 74,
    "termCode_id": "202612",
    "studentName": "Taylor Morgan",
    "studentSupervisee_id": "B12345765",
    "supervisor_id": "B12361006",
    "department_id": 1,
    "jobType": "Secondary",
    "WLS": 0,
    "POSN_TITLE": "Reception Assistant",
    "POSN_CODE": "S61416",
    "weeklyHours": 5,
    "startDate": "2027-01-15",
    "endDate": "2027-05-15"
}]).on_conflict_replace().execute()

FormHistory.insert([{
    "formHistoryID": 74,
    "formID_id": "74",
    "historyType_id": "Labor Status Form",
    "createdBy_id": 1,
    "createdDate": "2027-01-05",
    "status_id": "Approved"
}]).on_conflict_replace().execute()


# Student had a Fall-only position and receives a new Spring assignment.

LaborStatusForm.insert([{
    "laborStatusFormID": 75,
    "termCode_id": "202612",
    "studentName": "Jordan Brooks",
    "studentSupervisee_id": "B12345764",
    "supervisor_id": "B12361006",
    "department_id": 1,
    "jobType": "Primary",
    "WLS": 1,
    "POSN_TITLE": "Technology Assistant",
    "POSN_CODE": "S61423",
    "weeklyHours": 12,
    "startDate": "2027-01-15",
    "endDate": "2027-05-15"
}]).on_conflict_replace().execute()

FormHistory.insert([{
    "formHistoryID": 75,
    "formID_id": "75",
    "historyType_id": "Labor Status Form",
    "createdBy_id": 1,
    "createdDate": "2027-01-05",
    "status_id": "Approved"
}]).on_conflict_replace().execute()

LaborStatusForm.insert([{
    "laborStatusFormID": 76,
    "termCode_id": "202600",
    "studentName": "Jordan Brooks",
    "studentSupervisee_id": "B12345764",
    "supervisor_id": "B12361006",
    "department_id": 1,
    "jobType": "Secondary",
    "WLS": 1,
    "POSN_TITLE": "Technology Assistant",
    "POSN_CODE": "S61423",
    "weeklyHours": 10,
    "startDate": "2027-01-15",
    "endDate": "2027-05-15"
}]).on_conflict_replace().execute()

FormHistory.insert([{
    "formHistoryID": 76,
    "formID_id": "76",
    "historyType_id": "Labor Status Form",
    "createdBy_id": 1,
    "createdDate": "2027-01-05",
    "status_id": "Approved"
}]).on_conflict_replace().execute()


# Break Positions

LaborStatusForm.insert([{
    "laborStatusFormID": 67,
    "termCode_id": "202601",
    "studentName": "Jamie Foster",
    "studentSupervisee_id": "B12345767",
    "supervisor_id": "B12361006",
    "department_id": 1,
    "jobType": "Primary",
    "WLS": 1,
    "POSN_TITLE": "Thanksgiving Worker",
    "POSN_CODE": "S61418",
    "contractHours": 40,
    "startDate": "2026-11-22",
    "endDate": "2026-11-29"
}]).on_conflict_replace().execute()

LaborStatusForm.insert([{
    "laborStatusFormID": 68,
    "termCode_id": "202602",
    "studentName": "Riley Cooper",
    "studentSupervisee_id": "B12345768",
    "supervisor_id": "B12361006",
    "department_id": 1,
    "jobType": "Primary",
    "WLS": 1,
    "POSN_TITLE": "Christmas Worker",
    "POSN_CODE": "S61419",
    "contractHours": 120,
    "startDate": "2026-12-20",
    "endDate": "2027-01-03"
}]).on_conflict_replace().execute()

LaborStatusForm.insert([{
    "laborStatusFormID": 69,
    "termCode_id": "202603",
    "studentName": "Drew Bennett",
    "studentSupervisee_id": "B12345769",
    "supervisor_id": "B12361006",
    "department_id": 1,
    "jobType": "Primary",
    "WLS": 1,
    "POSN_TITLE": "Spring Break Worker",
    "POSN_CODE": "S61420",
    "contractHours": 80,
    "startDate": "2027-03-07",
    "endDate": "2027-03-14"
}]).on_conflict_replace().execute()

LaborStatusForm.insert([{
    "laborStatusFormID": 70,
    "termCode_id": "202604",
    "studentName": "Logan Price",
    "studentSupervisee_id": "B12345770",
    "supervisor_id": "B12361006",
    "department_id": 1,
    "jobType": "Primary",
    "WLS": 1,
    "POSN_TITLE": "Fall Break Worker",
    "POSN_CODE": "S61421",
    "contractHours": 24,
    "startDate": "2026-10-11",
    "endDate": "2026-10-18"
}]).on_conflict_replace().execute()

LaborStatusForm.insert([{
    "laborStatusFormID": 71,
    "termCode_id": "202613",
    "studentName": "Avery Sullivan",
    "studentSupervisee_id": "B12345771",
    "supervisor_id": "B12361006",
    "department_id": 1,
    "jobType": "Primary",
    "WLS": 1,
    "POSN_TITLE": "Summer Worker",
    "POSN_CODE": "S61422",
    "contractHours": 320,
    "startDate": "2027-05-15",
    "endDate": "2027-08-01"
}]).on_conflict_replace().execute()

FormHistory.insert([{
    "formHistoryID": 67,
    "formID_id": "67",
    "historyType_id": "Labor Status Form",
    "createdBy_id": 1,
    "createdDate": "2026-11-01",
    "status_id": "Approved"
}]).on_conflict_replace().execute()

FormHistory.insert([{
    "formHistoryID": 68,
    "formID_id": "68",
    "historyType_id": "Labor Status Form",
    "createdBy_id": 1,
    "createdDate": "2026-12-01",
    "status_id": "Approved"
}]).on_conflict_replace().execute()

FormHistory.insert([{
    "formHistoryID": 69,
    "formID_id": "69",
    "historyType_id": "Labor Status Form",
    "createdBy_id": 1,
    "createdDate": "2027-02-20",
    "status_id": "Approved"
}]).on_conflict_replace().execute()

FormHistory.insert([{
    "formHistoryID": 70,
    "formID_id": "70",
    "historyType_id": "Labor Status Form",
    "createdBy_id": 1,
    "createdDate": "2026-10-01",
    "status_id": "Approved"
}]).on_conflict_replace().execute()

FormHistory.insert([{
    "formHistoryID": 71,
    "formID_id": "71",
    "historyType_id": "Labor Status Form",
    "createdBy_id": 1,
    "createdDate": "2027-04-15",
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
    "department":       3,
    "isFinal":          False,
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
    "termCode":        202500,
    "department":       2,
    "isFinal":          False,
    "approvedOn":       None,
    "approvedBy":       None,
    "justification":    "Increase in student enrollment due to exodous from CS department",
    "primary_10":       4,
    "primary_12":       2,
    "primary_15":       7,
    "primary_20":       4,
    "secondary_5":      2,
    "secondary_10":     0,
    "breakHours":       750,
    },
    {
    "termCode":         202500,
    "department":       1,
    "isFinal":          False,
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
    "termCode":         202500,
    "department":       4,
    "isFinal":          False,
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
    "isFinal":          False,
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
    "department":       1,
    "isFinal":          True,
    "approvedOn":       None,
    "approvedBy":       None,
    "justification":    "Maintaining current staffing levels while allowing for moderate growth in student employment opportunities.",
    "primary_10":       6,
    "primary_12":       5,
    "primary_15":       4,
    "primary_20":       2,
    "secondary_5":      6,
    "secondary_10":     1,
    "breakHours":       600,
    },
                
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
        "revisionDate": f"2026-07-01",
        "revisedBy": "Mario Nakazawa",
        "department": 1
    },
    {
        
        "positionTitle": "Research Associate",
        "positionCode": "S61408",
        "status": "Active",
        "wls": 2,
        "revisionDate": f"2025-09-01",
        "revisionDate": f"2026-09-01",
        "revisedBy": "Deanna Wilborne",
        "department": 1
    },
    {
        "positionTitle": "Labor Workers",
        "positionCode": "S61409",
        "status": "Active",
        "wls": 3,
        "revisionDate": f"2026-07-01",
        "revisedBy": "Jasmine Jones",
        "department": 1
    },
    {
        "positionTitle": "Teaching Associate",
        "positionCode": "S61411",
        "status": "Active",
        "wls":3,
        "revisionDate" : f"2026-01-01",
        "revisedBy": "Scott Heggen",
        "department": 1

    },
    {
        "positionTitle": "Teaching Associate",
        "positionCode": "S61410",
        "status": "Inactive",
        "wls":2,
        "revisionDate" : f"2026-01-01",
        "revisedBy": "Brian Ramsay",
        "department" : 3
    },
    {
        "positionTitle": "Teaching Associate",
        "positionCode": "S61410",
        "status": "Active",
        "wls":2,
        "revisionDate" : f"2026-03-29",
        "revisedBy": "Jan Pearce",
        "department" : 3
    },
    {
        "positionTitle": "DUMMY POSITION",
        "positionCode": "S12345",
        "status": "Active",
        "wls":3,
        "revisionDate" : f"2026-01-23",
        "revisedBy": "Scott Heggen",
        "department" : 1
    },
    {
        "positionTitle": "Junior Data Analyst",
        "positionCode": "S39568",
        "status": "Active",
        "wls":4,
        "revisionDate" : f"2026-01-31",
        "revisedBy": "Jasmine Jones",
        "department" : 1
    },
    {
        "positionTitle": "Student Manager",
        "positionCode": "S74933",
        "status": "Active",
        "wls":5,
        "revisionDate" : f"2026-04-01",
        "revisedBy": "Deanna Wilborne",
        "department" : 1
    },
    {
        "positionTitle": "IT Technician",
        "positionCode": "S94932",
        "status": "Active",
        "wls":6,
        "revisionDate" : f"2026-05-03",
        "revisedBy": "Jan Pearce",
        "department" : 1
    },
    {
        "positionTitle": "Human code generator",
        "positionCode": "S22222",
        "status": "Active",
        "wls":1,
        "revisionDate" : f"2026-05-03",
        "revisedBy": "Jan Pearce",
        "department" : 1
    },
    {
        "positionTitle": "Senior Software Engineer",
        "positionCode": "S00000",
        "status": "Active",
        "wls":6,
        "revisionDate" : f"2026-05-03",
        "revisedBy": "Brian Ramsay",
        "department" : 1
    }
    
]
PositionHistory.insert_many(positionHistory).on_conflict_replace().execute()
print(" * position history added")

#############################
# Position Description Sections
#############################

positionDescriptionSections = [
    {
        "position": 2,
        "sectionTitle": '<h4>WLS Level Justification</h4>',
        "sectionContent": """
            <p>This position is assigned WLS 2 because it supports key research work with moderate technical complexity.</p>
        """,
        "order": 1,
    },
    {
        "position": 2,
        "sectionTitle": '<h4>Description of Duties</h4>',
        "sectionContent": """
            <p>Provide research assistance, coordinate data collection, and help prepare reports.</p>
        """,
        "order": 2,
    },
    {
        "position": 2,
        "sectionTitle": '<h4>Learning Opportunities</h4>',
        "sectionContent": """
            <p>Gain experience with research practices, data management, and academic collaboration.</p>
        """,
        "order": 3,
    },
    {
        "position": 2,
        "sectionTitle": '<h4>Required Qualifications</h4>',
        "sectionContent": """
            <p>Strong communication skills, attention to detail, and ability to work independently.</p>
        """,
        "order": 4,
    },
    {
        "position": 3,
        "sectionTitle": '<h4>WLS Level Justification</h4>',
        "sectionContent": """
            <p>Refer to the WLS Level definitions to describe why this level is appropriate for the role. Highlight supervision level, skill requirements, and scope of responsibility. This position assumes some previous experience on an FRC team or with software/programming. WLS Level 2 is appropriate for first-year students with some relevant experience or those new to Work-Learning-Service. It introduces students to professional habits, collaboration, and foundational technical tasks while providing structured guidance.</p>
        """,
        "order": 1,
    },
    {
        "position": 3,
        "sectionTitle": '<h4>Description of Duties</h4>',
        "sectionContent": """
            <h5>A. Workplace Responsibility</h5>
            <p>Follow team procedures for robot software development, daily check-ins, and documentation practices. Assist with organizing digital repositories and labeling source code for reuse and version control. Participate in sessions and preparations for outreach or competition in a timely and consistent manner.</p>

            <h5>B. Communication</h5>
            <p>Assist team leader(s) and student colleagues in planning lessons for FRC high school students, including researching materials and other investigations as assigned by team leader(s) with the goal of learning. Ask questions and provide updates on assigned coding or testing tasks.</p>

            <h5>C. Teamwork &amp; Collaboration</h5>
            <p>In collaboration with team leader(s), assist the team in supporting other student colleagues, generally overseeing high school students while working on and testing robot code.</p>

            <h5>D. Apply Critical Thinking and Problem Solving in Workplace Tasks</h5>
            <p>Attend the annual FRC competition and assist the team in supporting high school students in explaining and refining their software work and problem-solving skills under pressure. Identify and troubleshoot errors in logic, syntax, or structure in robot software projects.</p>

            <h5>E. Utilize Technology Effectively in the Workplace</h5>
            <p>In collaboration with team leader(s) and other student colleagues, assist high school students with projects and assignments related to the software of the robot.</p>

            <h5>F. Connect Work Experience to Career and Academic Goals</h5>
            <p>Train themselves with FIRST/Team resources in software to be competition-ready and prepare for the workforce (material provided by the supervisor).</p>

            <h5>G. Foster Creativity and Innovation in the Workplace</h5>
            <p>Help high school students stay engaged and safe while working with software tools (e.g., WPILib, VS Code, Git, GitHub, and Java) and during collaborative design reviews.</p>
        """,
        "order": 2,
    },
    {
        "position": 3,
        "sectionTitle": "<h4>Learning Opportunities</h4>",
        "sectionContent": """
            <p>List how this position will support student learning through daily responsibilities and intentional reflection. Supervisors are encouraged to reference specific Learning Goals (1–7) and describe how these goals show up in the work.</p>

            <h5>A. Peer Instruction and Facilitation</h5>
            <p>Gain experience in tutoring, lab assistance, and student mentorship. (Aligned with: Goals 2, 3, and 6)</p>

            <h5>B. Inventory and Resource Management</h5>
            <p>Track and maintain computer equipment and supplies effectively (e.g. update software regularly and install new relevant software). (Aligned with: Goals 1 and 4)</p>

            <h5>C. Problem Solving</h5>
            <p>Debugging code and testing said code on relevant robots. (Aligned with: Goal 3)</p>

            <h5>D. Technical Competency</h5>
            <p>Advance their knowledge of skills in specific areas of interest, namely software. (Aligned with: Goals 4 and 5)</p>

            <h5>E. Communication</h5>
            <p>Interaction with faculty, student colleagues, high school students, and their parents in a professional manner. (Aligned with: Goal 2)</p>
        """,
        "order": 3,
    },
    {
        "position": 3,
        "sectionTitle": "<h4>Required Qualifications</h4>",
        "sectionContent": """
            <p>List the baseline skills or attributes a student should have to be successful in this role, while ensuring equity and accessibility.</p>

            <h5>A. Independence</h5>
            <p>Ability to function with a little more independence and complete tasks with assistance from team leader(s) and other student colleagues.</p>

            <h5>B. Responsiveness to Feedback</h5>
            <p>Ability to take advice and respond appropriately.</p>

            <h5>C. Mentorship</h5>
            <p>A desire to mentor and work with high school students.</p>

            <h5>D. Patience</h5>
            <p>Patience working with unskilled yet energetic high school students.</p>

            <h5>E. Software Knowledge</h5>
            <p>Some basic understanding of software and debugging.</p>
        """,
    "order": 4,
    },
    {
        "position": 4,
        "sectionTitle": '<h4>WLS Level Justification</h4>',
        "sectionContent": """
            <p>Refer to the WLS Level definitions to describe why this level is appropriate for the role. Highlight supervision level, skill requirements, and scope of responsibility. This position assumes some previous experience on an FRC team or with software/programming. WLS Level 2 is appropriate for first-year students with some relevant experience or those new to Work-Learning-Service. It introduces students to professional habits, collaboration, and foundational technical tasks while providing structured guidance.</p>
        """,
        "order": 1,
    },
    {
        "position": 4,
        "sectionTitle": '<h4>Description of Duties</h4>',
        "sectionContent": """
            <h5>A. Workplace Responsibility</h5>
            <p>Follow team procedures for robot software development, daily check-ins, and documentation practices. Assist with organizing digital repositories and labeling source code for reuse and version control. Participate in sessions and preparations for outreach or competition in a timely and consistent manner.</p>

            <h5>B. Communication</h5>
            <p>Assist team leader(s) and student colleagues in planning lessons for FRC high school students, including researching materials and other investigations as assigned by team leader(s) with the goal of learning. Ask questions and provide updates on assigned coding or testing tasks.</p>

            <h5>C. Teamwork &amp; Collaboration</h5>
            <p>In collaboration with team leader(s), assist the team in supporting other student colleagues, generally overseeing high school students while working on and testing robot code.</p>

            <h5>D. Apply Critical Thinking and Problem Solving in Workplace Tasks</h5>
            <p>Attend the annual FRC competition and assist the team in supporting high school students in explaining and refining their software work and problem-solving skills under pressure. Identify and troubleshoot errors in logic, syntax, or structure in robot software projects.</p>

            <h5>E. Utilize Technology Effectively in the Workplace</h5>
            <p>In collaboration with team leader(s) and other student colleagues, assist high school students with projects and assignments related to the software of the robot.</p>

            <h5>F. Connect Work Experience to Career and Academic Goals</h5>
            <p>Train themselves with FIRST/Team resources in software to be competition-ready and prepare for the workforce (material provided by the supervisor).</p>

            <h5>G. Foster Creativity and Innovation in the Workplace</h5>
            <p>Help high school students stay engaged and safe while working with software tools (e.g., WPILib, VS Code, Git, GitHub, and Java) and during collaborative design reviews.</p>
        """,
        "order": 2,
    },
    {
        "position": 4,
        "sectionTitle": "<h4>Learning Opportunities</h4>",
        "sectionContent": """
            <p>List how this position will support student learning through daily responsibilities and intentional reflection. Supervisors are encouraged to reference specific Learning Goals (1–7) and describe how these goals show up in the work.</p>

            <h5>A. Peer Instruction and Facilitation</h5>
            <p>Gain experience in tutoring, lab assistance, and student mentorship. (Aligned with: Goals 2, 3, and 6)</p>

            <h5>B. Inventory and Resource Management</h5>
            <p>Track and maintain computer equipment and supplies effectively (e.g. update software regularly and install new relevant software). (Aligned with: Goals 1 and 4)</p>

            <h5>C. Problem Solving</h5>
            <p>Debugging code and testing said code on relevant robots. (Aligned with: Goal 3)</p>

            <h5>D. Technical Competency</h5>
            <p>Advance their knowledge of skills in specific areas of interest, namely software. (Aligned with: Goals 4 and 5)</p>

            <h5>E. Communication</h5>
            <p>Interaction with faculty, student colleagues, high school students, and their parents in a professional manner. (Aligned with: Goal 2)</p>
        """,
        "order": 3,
    },
    {
        "position": 4,
        "sectionTitle": "<h4>Required Qualifications</h4>",
        "sectionContent": """
            <p>List the baseline skills or attributes a student should have to be successful in this role, while ensuring equity and accessibility.</p>

            <h5>A. Independence</h5>
            <p>Ability to function with a little more independence and complete tasks with assistance from team leader(s) and other student colleagues.</p>

            <h5>B. Responsiveness to Feedback</h5>
            <p>Ability to take advice and respond appropriately.</p>

            <h5>C. Mentorship</h5>
            <p>A desire to mentor and work with high school students.</p>

            <h5>D. Patience</h5>
            <p>Patience working with unskilled yet energetic high school students.</p>

            <h5>E. Software Knowledge</h5>
            <p>Some basic understanding of software and debugging.</p>
        """,
        "order": 4,
    },
    {
        "position": 5,
        "sectionTitle": '<h4>WLS Level Justification</h4>',
        "sectionContent": """
            <p>Refer to the WLS Level definitions to describe why this level is appropriate for the role. Highlight supervision level, skill requirements, and scope of responsibility. This position assumes some previous experience on an FRC team or with software/programming. WLS Level 2 is appropriate for first-year students with some relevant experience or those new to Work-Learning-Service. It introduces students to professional habits, collaboration, and foundational technical tasks while providing structured guidance.</p>
        """,
        "order": 1,
    },
    {
        "position": 5,
        "sectionTitle": '<h4>Description of Duties</h4>',
        "sectionContent": """
            <h5>A. Workplace Responsibility</h5>
            <p>Follow team procedures for robot software development, daily check-ins, and documentation practices. Assist with organizing digital repositories and labeling source code for reuse and version control. Participate in sessions and preparations for outreach or competition in a timely and consistent manner.</p>

            <h5>B. Communication</h5>
            <p>Assist team leader(s) and student colleagues in planning lessons for FRC high school students, including researching materials and other investigations as assigned by team leader(s) with the goal of learning. Ask questions and provide updates on assigned coding or testing tasks.</p>

            <h5>C. Teamwork &amp; Collaboration</h5>
            <p>In collaboration with team leader(s), assist the team in supporting other student colleagues, generally overseeing high school students while working on and testing robot code.</p>

            <h5>D. Apply Critical Thinking and Problem Solving in Workplace Tasks</h5>
            <p>Attend the annual FRC competition and assist the team in supporting high school students in explaining and refining their software work and problem-solving skills under pressure. Identify and troubleshoot errors in logic, syntax, or structure in robot software projects.</p>

            <h5>E. Utilize Technology Effectively in the Workplace</h5>
            <p>In collaboration with team leader(s) and other student colleagues, assist high school students with projects and assignments related to the software of the robot.</p>

            <h5>F. Connect Work Experience to Career and Academic Goals</h5>
            <p>Train themselves with FIRST/Team resources in software to be competition-ready and prepare for the workforce (material provided by the supervisor).</p>

            <h5>G. Foster Creativity and Innovation in the Workplace</h5>
            <p>Help high school students stay engaged and safe while working with software tools (e.g., WPILib, VS Code, Git, GitHub, and Java) and during collaborative design reviews.</p>
        """,
        "order": 2,
    },
    {
        "position": 5,
        "sectionTitle": '<h4>Learning Opportunities</h4>',
        "sectionContent": """
            <p>List how this position will support student learning through daily responsibilities and intentional reflection. Supervisors are encouraged to reference specific Learning Goals (1–7) and describe how these goals show up in the work.</p>

            <h5>A. Peer Instruction and Facilitation</h5>
            <p>Gain experience in tutoring, lab assistance, and student mentorship. (Aligned with: Goals 2, 3, and 6)</p>

            <h5>B. Inventory and Resource Management</h5>
            <p>Track and maintain computer equipment and supplies effectively (e.g. update software regularly and install new relevant software). (Aligned with: Goals 1 and 4)</p>

            <h5>C. Problem Solving</h5>
            <p>Debugging code and testing said code on relevant robots. (Aligned with: Goal 3)</p>

            <h5>D. Technical Competency</h5>
            <p>Advance their knowledge of skills in specific areas of interest, namely software. (Aligned with: Goals 4 and 5)</p>

            <h5>E. Communication</h5>
            <p>Interaction with faculty, student colleagues, high school students, and their parents in a professional manner. (Aligned with: Goal 2)</p>
        """,
        "order": 3,
    },
    {
        "position": 5,
        "sectionTitle": '<h4>Required Qualifications</h4>',
        "sectionContent": """
            <p>List the baseline skills or attributes a student should have to be successful in this role, while ensuring equity and accessibility.</p>

            <h5>A. Independence</h5>
            <p>Ability to function with a little more independence and complete tasks with assistance from team leader(s) and other student colleagues.</p>

            <h5>B. Responsiveness to Feedback</h5>
            <p>Ability to take advice and respond appropriately.</p>

            <h5>C. Mentorship</h5>
            <p>A desire to mentor and work with high school students.</p>

            <h5>D. Patience</h5>
            <p>Patience working with unskilled yet energetic high school students.</p>

            <h5>E. Software Knowledge</h5>
            <p>Some basic understanding of software and debugging.</p>
        """,
        "order": 4,
    },
]

PositionDescriptionSection.insert_many(
    positionDescriptionSections
).on_conflict_replace().execute()

print(" * position description sections added")
