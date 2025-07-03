from app.logic.tracy import Tracy
from app.logic.tracy import InvalidQueryException
from peewee import DoesNotExist
from app.models.student import Student
from app.models.user import User


class InvalidUserException(Exception):
    pass

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
                            LAST_SUP_PIDM = tracyStudent.LAST_SUP_PIDM)
    else:
        raise InvalidUserException("Error: Could not get or create {0} {1}".format(tracyStudent.FIRST_NAME, tracyStudent.LAST_NAME))
    
