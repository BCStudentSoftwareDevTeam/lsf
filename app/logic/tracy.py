from app.config.loadConfig import get_secret_cfg
from peewee import DoesNotExist
import sqlalchemy
from app.models.Tracy import db
from app.models.Tracy.stuposn import STUPOSN
from app.models.Tracy.studata import STUDATA
from app.models.Tracy.stustaff import STUSTAFF
from app import app

class InvalidQueryException(Exception):
    pass

class Tracy():
    """
    A data access object for our Tracy queries.
    """

    def __init__(self):
        secret_conf = get_secret_cfg()

    #######################################

    def getStudents(self):
        """
        Return a list of student objects sorted alphabetically by first name
        """
        return STUDATA.query.order_by(STUDATA.FIRST_NAME).all()

    def getStudentFromBNumber(self, bnumber: str):
        """
        Return the student with the given B Number.

        Throws an InvalidQueryException if the B Number does not exist.
        """
        student = STUDATA.query.filter(sqlalchemy.func.trim(STUDATA.ID) == str(bnumber).strip()).first()
        if student is None:
            raise InvalidQueryException("B# {} not found in STUDATA".format(bnumber))

        return student

    def getStudentFromEmail(self, email: str):
        """
        Return the student with the given email.

        Throws an InvalidQueryException if the given email address does not exist.
        """
        student = STUDATA.query.filter(STUDATA.STU_EMAIL == email).first()
        if student is None:
            raise InvalidQueryException("Email {} not found in STUDATA".format(email))

        return student

    #######################################

    def getSupervisors(self):
        """
        Return a list of supervisor objects sorted alphabetically by first name
        """
        return STUSTAFF.query.order_by(STUSTAFF.FIRST_NAME).all()

    def getSupervisorFromID(self, id):
        """
        Return the supervisor with the given ID.

        Throws an InvalidQueryException if the given ID does not exist.
        """
        supervisor = STUSTAFF.query.filter(STUSTAFF.ID == id).first()
        if supervisor is None:
            raise InvalidQueryException("ID {} not found in STUSTAFF".format(id))

        return supervisor

    def getSupervisorFromEmail(self, email: str):
        """
        Return the supervisor with the given email.

        Throws an InvalidQueryException if the given email address does not exist.
        """
        supervisor = STUSTAFF.query.filter(STUSTAFF.EMAIL == email).first()
        if supervisor is None:
            raise InvalidQueryException("Email {} not found in STUSTAFF".format(email))

        return supervisor

    #######################################

    def getDepartments(self):
        """
        Return a list of departments, ordered by department name.
        """
        return STUPOSN.query.with_entities(STUPOSN.ORG, STUPOSN.DEPT_NAME, STUPOSN.ACCOUNT) \
                            .distinct().order_by(STUPOSN.DEPT_NAME).all()

    def getDepartmentsFromName(self, deptName):
        """
        Return a list of departments, ordered by department name.
        """
        return STUPOSN.query.with_entities(STUPOSN.ORG, STUPOSN.DEPT_NAME, STUPOSN.ACCOUNT) \
                            .filter(STUPOSN.DEPT_NAME == deptName).first()

    def getPositionsFromDepartment(self, departmentOrg: str, departmentAcct: str):
        """
        Return a list of position objects for the given department name, sorted by position title
        """
        return STUPOSN.query.filter((STUPOSN.ORG == departmentOrg) & (STUPOSN.ACCOUNT == departmentAcct)).order_by(STUPOSN.POSN_TITLE).all()

    def getPositionFromCode(self, positionCode: str):
        """
        Return the position for a given position code.
        """
        position = STUPOSN.query.get(positionCode)
        if position is None:
            raise InvalidQueryException("Position Code {} not found in STUPOSN".format(positionCode))

        return position

    def getSupervisorsFromUserInput(self, userInput: str):
        """
        Return a list of supervisors based off of the user input
        """
        userInput.strip()
        if " " not in userInput:
            supervisors = STUSTAFF.query.filter((STUSTAFF.FIRST_NAME.contains(userInput)) | (STUSTAFF.LAST_NAME.contains(userInput))).all()
        else:
            userInput = userInput.split()
            supervisors = STUSTAFF.query.filter((STUSTAFF.FIRST_NAME.contains(userInput[0])) & (STUSTAFF.LAST_NAME.contains(userInput[1]))).all()
        return supervisors

    def getStudentsFromUserInput(self, userInput: str):
        """
        Return a list of students based off of the user input
        """
        userInput.strip()
        if " " not in userInput:
            students = STUDATA.query.filter((STUDATA.FIRST_NAME.contains(userInput)) | (STUDATA.LAST_NAME.contains(userInput))).all()
        else:
            userInput = userInput.split()
            students = STUDATA.query.filter((STUDATA.FIRST_NAME.contains(userInput[0])) & (STUDATA.LAST_NAME.contains(userInput[1]))).all()
        return students

    def getStudentsFromBNumberSearch(self, bnum_part: str):
        """
        Return a list of students searching by bnumber
        """
        bnum_search = bnum_part.strip() + "%"
        students = STUDATA.query.filter(STUDATA.ID.like(bnum_search)).all()
        return students

    def checkStudentOrSupervisor(self, username: str):
        """
        Checks if the username belongs to a student or supervisor
        """
        email = "{}@berea.edu".format(username)
        try:
            supervisor = self.getSupervisorFromEmail(email)
            if supervisor:
                return "Supervisor"
        except:
            student = self.getStudentFromEmail(email)
            if student:
                return "Student"
