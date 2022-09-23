from app.models.student import Student
from app.models.laborStatusForm import LaborStatusForm
from app.models.department import Department
from app.models.formHistory import FormHistory

def limitSearch(students, currentUser):
    """ Given a list of student dictionaries and the currentUser the function will only return a
    list of students who have held a labor position within the currentUsers department."""
    newstudents = []
    # Query returns a list of all departments the currentUser has either been a supervisor or created an LSF for.
    departments = list(Department.select(Department.departmentID)
                    .join_from(Department, LaborStatusForm)
                    .join_from(LaborStatusForm, FormHistory)
                    .where((LaborStatusForm.supervisor == currentUser.supervisor.ID) | (FormHistory.createdBy == currentUser))
                    .distinct()
                    )
    # Query returns a list of student objects for every student who has worked in the departments returned by the "departments" query.
    students_in_department = list(Student.select(Student.ID)
                .join_from(Student, LaborStatusForm)
                .join_from(LaborStatusForm, Department)
                .where(Department.departmentID.in_(departments))
                .distinct())
    studentBnumbers = [student.ID for student in students_in_department]
    newstudents = list(filter(lambda student: student['bnumber'] in studentBnumbers, students))

    return newstudents

def usernameFromEmail(email):
    # split always returns a list, even if there is nothing to split, so [0] is safe
    return email.split('@',1)[0]

# Convert a Student or STUDATA record into the dictionary that our js expects
def studentDbToDict(item):
    return {'username': usernameFromEmail(item.STU_EMAIL.strip()),
            'firstName': item.FIRST_NAME.strip(),
            'lastName': item.LAST_NAME.strip(),
            'bnumber': item.ID.strip(),
            'type': 'Student'}
