from app.models.student import Student
from app.models.laborStatusForm import LaborStatusForm
from app.models.department import Department
from app.models.formHistory import FormHistory

def limitSearch(students, currentUser):
    newstudents = []
    departments = list(FormHistory.select(FormHistory.formID.department)
                    .join_from(FormHistory, LaborStatusForm)
                    .join_from(LaborStatusForm, Department)
                    .where((FormHistory.formID.supervisor == currentUser.supervisor.ID) | (FormHistory.createdBy == currentUser))
                    .distinct()
                    )
    print([i.formID.department for i in departments])
    for student in students:
        print(student)
        student_in_department = list(FormHistory.select(FormHistory.formID.department)
                    .join_from(FormHistory, LaborStatusForm)
                    .join_from(LaborStatusForm, Department)
                    .where(FormHistory.formID.studentSupervisee == student['bnumber'], FormHistory.formID.department.in_(departments))
                    .distinct()
                    )
        print([s for s in student_in_department])
        if len(student_in_department) > 0:
            newstudents.append(student)

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
