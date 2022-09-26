import pytest
from app.models import mainDB
from app.models.department import Department
from app.models.student import Student
from app.models.supervisor import Supervisor
from app.models.laborStatusForm import LaborStatusForm
from app.models.formHistory import FormHistory
from app.models.user import User
from peewee import DoesNotExist
from app.logic.search import limitSearch, studentDbToDict,getDepartmentsForSupervisor

@pytest.mark.integration
def test_limitSearch():
    with mainDB.atomic() as transaction:
        # intialize departments for testing
        supervisorDept = Department.create(DEPT_NAME="supervisorDept", ACCOUNT="6740", ORG="2114", departmentCompliance = 1)
        unattachedDept = Department.create(DEPT_NAME="Not SupervisorDept", ACCOUNT="6740", ORG="2114", departmentCompliance = 1)

        # initialize students for testing
        inDeptStudent = Student.create(ID = "B10701360",
                                       PIDM = 3,
                                       FIRST_NAME = "Tyler",
                                       LAST_NAME = "Parton",
                                       CLASS_LEVEL = "Senior",
                                       STU_EMAIL = "partont@berea.edu")

        outDeptStudent = Student.create(ID = "B00000000",
                                        PIDM = 4,
                                        FIRST_NAME = "Not",
                                        LAST_NAME = "Tyler",
                                        CLASS_LEVEL = "Not a Senior",
                                        STU_EMAIL = "tylern@berea.edu")

        # intitialize supervisor for testing
        outOfDeptSuper = Supervisor.create(ID = "B00000001",
                                           PIDM = 75,
                                           FIRST_NAME = "Not",
                                           LAST_NAME = "Scott",
                                           EMAIL = "None",
                                           CPO = "None",
                                           DEPT_NAME = "Biology")

        outOfDeptSuperUser = User.create(student = None,
                                         supervisor = outOfDeptSuper.ID,
                                         username = "scottn",
                                         isLaborAdmin = None,
                                         isFinancialAidAdmin = None,
                                         isSaasAdmin = None)

        # intialize labor status forms
        inDeptForm = LaborStatusForm.create(StudentName = "Tyler Parton",
                                            termCode = 202000,
                                            studentSupervisee = "B10701360",
                                            supervisor = "B00763721",
                                            department = 1,
                                            jobType = "Primary",
                                            WLS = "1",
                                            POSN_TITLE = "Student Programmer",
                                            POSN_CODE = "S61407")

        outDeptForm = LaborStatusForm.create(StudentName = "Not Tyler",
                                             termCode = 202000,
                                             studentSupervisee = "B00000000",
                                             supervisor = "B00000001",
                                             department = 4,
                                             jobType = "Primary",
                                             WLS = "1",
                                             POSN_TITLE = "Student Programmer",
                                             POSN_CODE = "S61409")

        # intialize form history for testing
        inDeptFormHistory = FormHistory.create(formID = inDeptForm.laborStatusFormID,
                                               historyType = "Labor Status Form",
                                               releaseForm = None,
                                               adjustedForm = None,
                                               overloadForm = None,
                                               createdBy = 1,
                                               createdDate = "2020-04-14",
                                               reviewedDate = None,
                                               reviewedBy = None,
                                               status = "Approved")

        outDeptFormHistory = FormHistory.create(formID = outDeptForm.laborStatusFormID,
                                                historyType = "Labor Status Form",
                                                releaseForm = None,
                                                adjustedForm = None,
                                                overloadForm = None,
                                                createdBy = outOfDeptSuperUser.userID,
                                                createdDate = "2020-04-14",
                                                reviewedDate = None,
                                                reviewedBy = None,
                                                status = "Approved")

        students = [inDeptStudent, outDeptStudent]
        students_converted = [studentDbToDict(student) for student in students]
        newStudents = limitSearch(students_converted, outOfDeptSuperUser)

        assert students_converted[0] not in newStudents
        assert students_converted[1] in newStudents

        transaction.rollback()

@pytest.mark.integration
def test_getDepartmentsForSupervisors():
    with mainDB.atomic() as transaction:

        supervisorDept = Department.create(DEPT_NAME="supervisorDept", ACCOUNT="6740", ORG="2114", departmentCompliance = 1)

        nonSupervisorDept = Department.create(DEPT_NAME="nonSupervisorDept", ACCOUNT="6740", ORG="9992", departmentCompliance = 1)

        tempSuper = Supervisor.create(ID = "B00000002",
                                           PIDM = 75,
                                           FIRST_NAME = "Not",
                                           LAST_NAME = "Scott",
                                           EMAIL = "None",
                                           CPO = "None",
                                           DEPT_NAME = "Biology")

        tempSuperUser = User.create(student = None,
                                         supervisor = tempSuper.ID,
                                         username = "scottn",
                                         isLaborAdmin = None,
                                         isFinancialAidAdmin = None,
                                         isSaasAdmin = None)

        tempStudent = Student.create(ID = "B99999999",
                                     PIDM = 97,
                                     FIRST_NAME = "Tyler",
                                     LAST_NAME = "Parton",
                                     CLASS_LEVEL = "Senior",
                                     STU_EMAIL = "partont@berea.edu")

        supervisor = Supervisor.create(ID = "B00000001",
                                       PIDM = 75,
                                       FIRST_NAME = "Not",
                                       LAST_NAME = "Scott",
                                       EMAIL = "None",
                                       CPO = "None",
                                       DEPT_NAME = "supervisorDept")

        supervisorUser = User.create(student = None,
                                     supervisor = supervisor.ID,
                                     username = "scottn",
                                     isLaborAdmin = None,
                                     isFinancialAidAdmin = None,
                                     isSaasAdmin = None)

        lsf1 = LaborStatusForm.create(StudentName = "Tyler Parton",
                                        termCode = 202000,
                                        studentSupervisee = "B99999999",
                                        supervisor = "B00000001",
                                        department = supervisorDept.departmentID,
                                        jobType = "Primary",
                                        WLS = "1",
                                        POSN_TITLE = "Student Programmer",
                                        POSN_CODE = "S61407")

        lsf2 = LaborStatusForm.create(StudentName = "Tyler Parton",
                                        termCode = 202000,
                                        studentSupervisee = "B99999999",
                                        supervisor = "B00000002",
                                        department = nonSupervisorDept.departmentID,
                                        jobType = "Primary",
                                        WLS = "1",
                                        POSN_TITLE = "Student Programmer",
                                        POSN_CODE = "S61407")

        formHistory = FormHistory.create(formID = lsf2.laborStatusFormID,
                                         historyType = "Labor Status Form",
                                         releaseForm = None,
                                         adjustedForm = None,
                                         overloadForm = None,
                                         createdBy = supervisorUser.userID,
                                         createdDate = "2020-04-14",
                                         reviewedDate = None,
                                         reviewedBy = None,
                                         status = "Approved")

        departments = list(getDepartmentsForSupervisor(supervisorUser))
        departments = [i.DEPT_NAME for i in departments]
        assert supervisorDept.DEPT_NAME in departments
        assert nonSupervisorDept.DEPT_NAME in departments

        transaction.rollback()
