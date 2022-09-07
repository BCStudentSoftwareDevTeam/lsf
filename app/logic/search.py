from app.models.student import Student
from app.models.laborStatusForm import LaborStatusForm
from app.models.department import Department
from app.models.formHistory import FormHistory

def limitSearch(students):
    newstudents = []
    departments = list(FormHistory.select()
                    .join_from(FormHistory, LaborStatusForm)
                    .join_from(LaborStatusForm, Department)
                    .where((FormHistory.formID.supervisor == currentUser.supervisor.ID) | (FormHistory.createdBy == currentUser))
                    .distinct()
                    )
    # for d in departments:
    #     print(d.formID.department.DEPT_NAME)
    for student in students:
        student_in_department = (FormHistory.select()
                    .join_from(FormHistory, LaborStatusForm)
                    .join_from(LaborStatusForm, Department)
                    .where((FormHistory.formID.studentSupervisee == student['bnumber']) & FormHistory in departments)
                    .distinct()
                    )

        for d in student_in_department:
            print(d.formID.department.DEPT_NAME)
        if student_in_department:
            newstudents.append(student)

            return newstudents
