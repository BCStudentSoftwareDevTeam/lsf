from app.models.student import Student
from app.models.supervisor import Supervisor
from app.models.laborStatusForm import LaborStatusForm
from app.models.department import Department
from app.models.formHistory import FormHistory

def limitSearch(students, currentUser):
    """
    Given a list of student dictionaries and the currentUser the function will only return a
    list of students who have held a labor position within the currentUsers department.
    """
    newstudents = []
    # Query returns a list of all departments the currentUser has either been a supervisor or created an LSF for.
    departments = list(getDepartmentsForSupervisor(currentUser))
    # convert department objects to ids
    departments = [department.departmentID for department in departments]
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
def studentDbToDict(student):
    """
    Given a student object it will return a mapped Dict with student data.
    """
    return {'username': usernameFromEmail(student.STU_EMAIL.strip()),
            'firstName': student.FIRST_NAME.strip(),
            'lastName': student.LAST_NAME.strip(),
            'bnumber': student.ID.strip(),
            'type': 'Student'}

def getDepartmentsForSupervisor(currentUser):
    """
    Given currentUser, find and return all departments that the user is associated with.
    """
    departments = (Department.select()
                    .join_from(Department, LaborStatusForm)
                    .join_from(LaborStatusForm, FormHistory)
                    .join_from(LaborStatusForm, Supervisor)
                    .where((LaborStatusForm.supervisor.ID == currentUser.supervisor.ID) | (FormHistory.createdBy == currentUser)).order_by(Department.DEPT_NAME)
                    .distinct()
                    )

    return departments