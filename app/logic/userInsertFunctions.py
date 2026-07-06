from datetime import datetime, date, timedelta, time
from functools import reduce
from peewee import DoesNotExist

from app.models.user import *
from app.models.status import *
from app.models.laborStatusForm import *
from app.models.overloadForm import *
from app.models.formHistory import*
from app.models.historyType import *
from app.models.term import *
from app.models.student import Student
from app.models.supervisor import Supervisor
from app.models.department import *
from app.logic.tracy import Tracy, InvalidQueryException, InvalidUserException


def updatePersonRecords():
    """
    This function will update all student and supervisor records according to
    Tracy data.
    """
    studentsInDB = Student.select()
    supervisorsInDB = Supervisor.select()
    studentsFound = 0
    studentsNotFound = 0
    studentsFailed = 0
    supervisorsFound = 0
    supervisorsNotFound = 0
    supervisorsFailed = 0
    for student in studentsInDB:
        try:
            updateStudentRecord(student)
            studentsFound = studentsFound + 1
        except InvalidQueryException as e:
            student.isActive=False
            student.save()
            studentsNotFound = studentsNotFound + 1
        except Exception as e:
            studentsFailed += 1
    for supervisor in supervisorsInDB:
        try:
            supervisor.isActive = False
            updateSupervisorRecord(supervisor)
            supervisorsFound = supervisorsFound + 1
        except InvalidQueryException as e:
            supervisorsNotFound = supervisorsNotFound + 1
        except Exception as e:
            supervisorsFailed = supervisorsFailed + 1
    return studentsFound, studentsNotFound, studentsFailed, supervisorsFound, supervisorsNotFound, supervisorsFailed



def updateUserFromTracy(user):
    """
        Takes user object and determines if it is a student user or a supervisor user and will
        update the DB accordingly.
    """
    try:
        tracyUser = None
        baseObj = None
        if user.student:
            tracyUser = Tracy().getStudentFromBNumber(user.student_id)
            baseObj = user.student
        if user.supervisor:
            tracyUser = Tracy().getSupervisorFromID(user.supervisor_id)
            baseObj = user.supervisor

        baseObj.legal_name = tracyUser.FIRST_NAME
        baseObj.LAST_NAME = tracyUser.LAST_NAME
        baseObj.save()

    except Exception as e:
        print( f"We don't want to break our login if an old tracy user doesn't exist or something")

    return user

def updateStudentRecord(student):
    """This function will update all student fields to match Tracy data."""
    tracyUser = Tracy().getStudentFromBNumber(student.ID)

    student.legal_name = tracyUser.FIRST_NAME
    student.LAST_NAME = tracyUser.LAST_NAME
    student.CLASS_LEVEL = tracyUser.CLASS_LEVEL
    student.ACADEMIC_FOCUS = tracyUser.ACADEMIC_FOCUS
    student.MAJOR = tracyUser.MAJOR
    student.PROBATION = tracyUser.PROBATION
    student.ADVISOR = tracyUser.ADVISOR
    student.STU_EMAIL = tracyUser.STU_EMAIL
    student.STU_CPO = tracyUser.STU_CPO
    student.LAST_POSN = tracyUser.LAST_POSN
    student.LAST_SUP_PIDM = tracyUser.LAST_SUP_PIDM
    student.isActive=True
    student.save()

def updateSupervisorRecord(supervisor):
    """This function will update all supervisor fields to match Tracy data."""
    tracyUser = Tracy().getSupervisorFromID(supervisor.ID)

    supervisor.PIDM = tracyUser.PIDM
    supervisor.legal_name = tracyUser.FIRST_NAME
    supervisor.LAST_NAME = tracyUser.LAST_NAME
    supervisor.EMAIL = tracyUser.EMAIL
    supervisor.CPO = tracyUser.CPO
    supervisor.ORG = tracyUser.ORG
    supervisor.DEPT_NAME = tracyUser.DEPT_NAME
    supervisor.isActive = True
    supervisor.save()



def createUser(username, student=None, supervisor=None):
    """
    Retrieves or creates a user in the User table and updates Supervisor and/or Student as requested.

    Raises InvalidUserException if this does not succeed.
    """

    if not student and not supervisor:
        raise InvalidUserException("A User should be connected to Student or Supervisor")

    try:
        user = User.get_or_create(username=username)[0]

    except Exception as e:
        raise InvalidUserException("Adding {} to user table failed".format(username), e)

    if student:
        user.student = student.ID # Not sure why assigning the object doesn't work...
    if supervisor:
        user.supervisor = supervisor.ID

    user.save()

    return user

def getOrCreateStudentRecord(username=None, bnumber=None):
    """
        Attempts to add a student from the Tracy database to the application, based on the provided username or bnumber.
        Raises InvalidUserException if this does not succeed.
    """
    if not username and not bnumber:
        raise ValueError("No arguments provided to getOrCreateStudentRecord()")
    try:
        if bnumber:
            student = Student.get(Student.ID == bnumber)
        else:
            student = Student.get(Student.STU_EMAIL == "{}@berea.edu".format(username))
    except DoesNotExist:
        student = createStudentFromTracy(username,bnumber)
    return student



def createStudentFromTracy(username=None, bnumber=None):
    """
        Attempts to add a student from the Tracy database to the application, based on the provided username or bnumber.

        Raises InvalidUserException if this does not succeed.
    """
    if not username and not bnumber:
        raise ValueError("No arguments provided to createStudentFromTracy()")

    if bnumber:
        try:
            tracyStudent = Tracy().getStudentFromBNumber(bnumber)
        except InvalidQueryException as e:
            raise InvalidUserException("{} not found in Tracy database".format(bnumber))

    else:    # Executes if no ID is provided
        email = "{}@berea.edu".format(username)
        try:
            tracyStudent = Tracy().getStudentFromEmail(email)
        except InvalidQueryException as e:
            raise InvalidUserException("{} not found in Tracy database".format(email))

    # Create the student in Tracy
    try:
        return Student.get(Student.ID == tracyStudent.ID.strip())
    except DoesNotExist:
        #print('Could not find {0} {1} in Student table, creating new entry.'.format(tracyStudent.FIRST_NAME, tracyStudent.LAST_NAME))
        return Student.create(ID = tracyStudent.ID.strip(),
                            PIDM = tracyStudent.PIDM,
                            legal_name = tracyStudent.FIRST_NAME,
                            LAST_NAME = tracyStudent.LAST_NAME,
                            CLASS_LEVEL = tracyStudent.CLASS_LEVEL,
                            ACADEMIC_FOCUS = tracyStudent.ACADEMIC_FOCUS,
                            MAJOR = tracyStudent.MAJOR,
                            PROBATION = tracyStudent.PROBATION,
                            ADVISOR = tracyStudent.ADVISOR,
                            STU_EMAIL = tracyStudent.STU_EMAIL,
                            STU_CPO = tracyStudent.STU_CPO,
                            LAST_POSN = tracyStudent.LAST_POSN,
                            LAST_SUP_PIDM = tracyStudent.LAST_SUP_PIDM,
                            isActive=True)
    else:
        raise InvalidUserException("Error: Could not get or create {0} {1}".format(tracyStudent.FIRST_NAME, tracyStudent.LAST_NAME))


def createSupervisorFromTracy(username=None, bnumber=None):
    """
        Attempts to add a supervisor from the Tracy database to the application, based on the provided username or bnumber.

        Raises InvalidUserException if this does not succeed.
    """
    if bnumber:
        try:
            tracyUser = Tracy().getSupervisorFromID(bnumber)
        except InvalidQueryException as e:
            raise InvalidUserException("{} not found in Tracy database".format(bnumber))

    else:    # Executes if no ID is provided
        email = "{}@berea.edu".format(username)
        try:
            tracyUser = Tracy().getSupervisorFromEmail(email)
        except InvalidQueryException as e:
            raise InvalidUserException("{} not found in Tracy database".format(email))

    try:
        return Supervisor.get(Supervisor.ID == tracyUser.ID.strip())
    except DoesNotExist:
        return Supervisor.create(PIDM = tracyUser.PIDM,
                                 legal_name = tracyUser.FIRST_NAME,
                                 LAST_NAME = tracyUser.LAST_NAME,
                                 ID = tracyUser.ID.strip(),
                                 EMAIL = tracyUser.EMAIL,
                                 CPO = tracyUser.CPO,
                                 ORG = tracyUser.ORG,
                                 DEPT_NAME = tracyUser.DEPT_NAME,
                                 isActive=True)
    except Exception as e:
        print(e)
        raise InvalidUserException("Error: Could not get or create {0} {1}".format(tracyUser.FIRST_NAME, tracyUser.LAST_NAME))
