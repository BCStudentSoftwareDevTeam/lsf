import pytest
from app.models import mainDB
from app.models.department import Department
from app.models.student import Student
from app.models.supervisor import Supervisor
from app.models.supervisorDepartment import SupervisorDepartment
from app.models.laborStatusForm import LaborStatusForm
from app.models.formHistory import FormHistory
from app.models.user import User
from peewee import DoesNotExist
from app.logic.search import limitSearchByUserDepartment, studentDbToDict,getDepartmentsForSupervisor

@pytest.mark.integration
def test_limitSearchByUserDepartment():
    with mainDB.atomic() as transaction:
        # intialize departments for testing
        supervisorDept = Department.create(DEPT_NAME="supervisorDept", ACCOUNT="6740", ORG="2114", departmentCompliance = 1)
        unattachedDept = Department.create(DEPT_NAME="Not SupervisorDept", ACCOUNT="6740", ORG="2114", departmentCompliance = 1)

        # initialize students for testing
        inDeptStudent = Student.create(ID = "B10701360",
                                       PIDM = 3,
                                       legal_name = "Tyler",
                                       LAST_NAME = "Parton",
                                       CLASS_LEVEL = "Senior",
                                       STU_EMAIL = "partont@berea.edu")

        outDeptStudent = Student.create(ID = "B00000000",
                                        PIDM = 4,
                                        legal_name = "Not",
                                        LAST_NAME = "Tyler",
                                        CLASS_LEVEL = "Not a Senior",
                                        STU_EMAIL = "tylern@berea.edu")

        # intitialize supervisor for testing
        outOfDeptSuper = Supervisor.create(ID = "B00000001",
                                           PIDM = 75,
                                           legal_name = "Not",
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
        newStudents = limitSearchByUserDepartment(students_converted, outOfDeptSuperUser)

        assert students_converted[0] not in newStudents
        assert students_converted[1] in newStudents

        transaction.rollback()

@pytest.mark.integration
def test_getDepartmentsForSupervisors():
    with mainDB.atomic() as transaction:

        supervisorDept = Department.create(DEPT_NAME="supervisorDept", ACCOUNT="6740", ORG="2114", departmentCompliance = 1)

        nonSupervisorDept = Department.create(DEPT_NAME="nonSupervisorDept", ACCOUNT="6740", ORG="9992", departmentCompliance = 1)

        supervisorTableTestDept = Department.create(DEPT_NAME="testTable", ACCOUNT="6740", ORG="9998", departmentCompliance = 1)


        # Supervisor create so we can check when our superUser is the creator but tempSuper is the supervisor.
        tempSuper = Supervisor.create(ID = "B00000002",
                                           PIDM = 75,
                                           legal_name = "Not",
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
                                     legal_name = "Tyler",
                                     LAST_NAME = "Parton",
                                     CLASS_LEVEL = "Senior",
                                     STU_EMAIL = "partont@berea.edu")

        supervisor = Supervisor.create(ID = "B00000001",
                                       PIDM = 75,
                                       legal_name = "Not",
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

        # Form in which our superUser is the supervisor and not the creator.
        lsf1 = LaborStatusForm.create(StudentName = "Tyler Parton",
                                        termCode = 202000,
                                        studentSupervisee = "B99999999",
                                        supervisor = supervisor.ID,
                                        department = supervisorDept.departmentID,
                                        jobType = "Primary",
                                        WLS = "1",
                                        POSN_TITLE = "Student Programmer",
                                        POSN_CODE = "S61407")

        #Form in which our superUser is the creator and not the supervisor.
        lsf2 = LaborStatusForm.create(StudentName = "Tyler Parton",
                                        termCode = 202000,
                                        studentSupervisee = "B99999999",
                                        supervisor = "B00000002",
                                        department = nonSupervisorDept.departmentID,
                                        jobType = "Primary",
                                        WLS = "1",
                                        POSN_TITLE = "Student Programmer",
                                        POSN_CODE = "S61407")

        #Need formhistory for the query to check against.
        formCreator = FormHistory.create(formID = lsf2.laborStatusFormID,
                                         historyType = "Labor Status Form",
                                         releaseForm = None,
                                         adjustedForm = None,
                                         overloadForm = None,
                                         createdBy = supervisorUser.userID,
                                         createdDate = "2020-04-14",
                                         reviewedDate = None,
                                         reviewedBy = None,
                                         status = "Approved")

        formNonCreator = FormHistory.create(formID = lsf1.laborStatusFormID,
                                         historyType = "Labor Status Form",
                                         releaseForm = None,
                                         adjustedForm = None,
                                         overloadForm = None,
                                         createdBy = tempSuperUser.userID,
                                         createdDate = "2020-04-14",
                                         reviewedDate = None,
                                         reviewedBy = None,
                                         status = "Approved")


        departments = list(getDepartmentsForSupervisor(supervisorUser))
        departments = [i.DEPT_NAME for i in departments]
        assert supervisorDept.DEPT_NAME in departments
        assert nonSupervisorDept.DEPT_NAME in departments

        supervisorDeptTable = SupervisorDepartment.create(supervisor=supervisorUser.supervisor.ID,
                                                    department=supervisorTableTestDept)

        # check to make sure we get both the departments that a user interacted with and departments in the tavle
        departments = list(getDepartmentsForSupervisor(supervisorUser))
        departments = [i.DEPT_NAME for i in departments]
        assert supervisorDeptTable.department.DEPT_NAME in departments
        assert len(departments) == 3

        # add existing department to table
        SupervisorDepartment.create(supervisor=supervisorUser.supervisor.ID,
                                    department=supervisorDept)

        # make sure that a department is not duplicated if it is in the table and a user has forms for its
        departments = list(getDepartmentsForSupervisor(supervisorUser))
        assert len(departments) == 3

        transaction.rollback()
