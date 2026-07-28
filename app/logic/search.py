from app.models.student import Student
from app.models.supervisor import Supervisor
from app.models.supervisorDepartment import SupervisorDepartment
from app.models.laborStatusForm import LaborStatusForm
from app.models.department import Department
from app.models.formHistory import FormHistory
from app.models.term import Term

from functools import reduce
import operator
from peewee import JOIN

def limitSearchByUserDepartment(students, currentUser):
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
    dbToDict =  {'username': usernameFromEmail(student.STU_EMAIL.strip()),
                'firstName': student.FIRST_NAME.strip(),
                'lastName': student.LAST_NAME.strip(),
                'bnumber': student.ID.strip(),
                'type': 'Student'}
    return dbToDict

def getAssignedDepartments(currentUser):
    """
    Given currentUser, return only the departments the user is directly assigned to
    supervise (per the SupervisorDepartment table). Unlike getDepartmentsForSupervisor,
    this does not include departments the user has merely interacted with via forms, so
    it's the correct set to use for authorization checks.
    """
    return Department.select().join(SupervisorDepartment).where(SupervisorDepartment.supervisor == currentUser.supervisor)

def getDepartmentsForSupervisor(currentUser):
    """
    Given currentUser, find and return all departments that the user is associated with.
    """
    supervisorDepts = getAssignedDepartments(currentUser)

    # queries all forms to see what departments the user has interacted with
    departments = (Department.select(Department)
                    .join_from(Department, LaborStatusForm)
                    .join_from(LaborStatusForm, FormHistory)
                    .join_from(LaborStatusForm, Supervisor)
                    .where((LaborStatusForm.supervisor.ID == currentUser.supervisor.ID) | (FormHistory.createdBy == currentUser)).order_by(Department.DEPT_NAME)
                    .distinct()
                    )
    alldepts = departments.union(supervisorDepts)
    return alldepts

def isDepartmentAllowed(currentUser, department):
    """
    Given currentUser and a department, return True if the user is allowed to access it
    (labor admins are always allowed; supervisors only for departments they're directly
    assigned to, not merely departments they've interacted with via forms).
    """
    if currentUser.isLaborAdmin:
        return True
    return department in getAssignedDepartments(currentUser)

def getSupervisorsForDepartment(departmentId):
    departmentSupervisors = Supervisor.select().join(SupervisorDepartment).where(SupervisorDepartment.department == departmentId).order_by(Supervisor.LAST_NAME).execute()
    return departmentSupervisors

def searchSupervisorPortal(currentUser, searchType, userInput):
    if currentUser.isLaborAdmin or currentUser.isFinancialAidAdmin or currentUser.isSaasAdmin:
        allowed_departments = None  # unrestricted
    else:
        allowed_departments = [dept.DEPT_NAME for dept in getDepartmentsForSupervisor(currentUser)]

    if searchType == "termSelect":
        terms = Term.select().where(Term.termName.contains(userInput)).order_by(Term.termCode.desc())
        return [{'termCode': term.termCode, 'termName': term.termName} for term in terms]

    elif searchType == "departmentSelect":
        query = Department.select().where(Department.DEPT_NAME.contains(userInput))
        if allowed_departments is not None:
            query = query.where(Department.DEPT_NAME.in_(allowed_departments))
        query = query.order_by(Department.isActive.desc(), Department.DEPT_NAME.asc()).limit(10)
        return [
            {'DEPT_NAME': dept.DEPT_NAME, 'id': dept.departmentID, 'isActive': dept.isActive} 
            for dept in query
        ]

    elif searchType == "supervisorSelect":
        supervisor_query = searchPerson(Supervisor, userInput, allowed_departments)
        supervisor_query = supervisor_query.order_by(Supervisor.isActive.desc()).limit(10)
        return [
            {'id': sup.ID, 'FIRST_NAME': sup.FIRST_NAME, "LAST_NAME": sup.LAST_NAME, "isActive": sup.isActive} 
            for sup in supervisor_query
        ]

    elif searchType == "studentSelect":
        student_query = searchPerson(Student, userInput, allowed_departments)
        student_query = student_query.order_by(Student.LAST_NAME.asc()).limit(10)
        return [
            {'id': stu.ID, 'FIRST_NAME': stu.FIRST_NAME, 'LAST_NAME': stu.LAST_NAME} 
            for stu in student_query
        ]

    return []

def searchPerson(model, userInput, allowed_departments=None):
    """
    Returns a Peewee SelectObject filtered so that all words in userInput
    must appear in at least one of the model's fields.
    """
    words = userInput.strip().split()

    word_conditions = []
    for word in words:
        word_conditions.append(
            (model.preferred_name.contains(word)) |
            (model.legal_name.contains(word)) |
            (model.LAST_NAME.contains(word)) |
            (model.ID.contains(word))
        )

    query = model.select().where(reduce(operator.and_, word_conditions))

    if allowed_departments is not None:
        query = (
            query
            .join_from(model, LaborStatusForm, JOIN.LEFT_OUTER)
            .join_from(LaborStatusForm, Department, JOIN.LEFT_OUTER)
            .where(Department.DEPT_NAME.in_(allowed_departments))
            .distinct()
        )

    return query