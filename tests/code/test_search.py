import pytest
from app.models import mainDB
from app.models.department import Department
from app.models.student import Student
from app.models.supervisor import Supervisor
from app.models.laborStatusForm import LaborStatusForm
from app.models.formHistory import FormHistory
from app.models.user import User
from peewee import DoesNotExist
from app.logic.search import limitSearch, studentDbToDict, usernameFromEmail

@pytest.mark.integration
def test_search():
    with mainDB.atomic() as transaction:
        # intialize departments for testing
        supervisorDept = Department.create(DEPT_NAME="supervisorDept", ACCOUNT="6740", ORG="2114", departmentCompliance = 1)
        unattachedDept = Department.create(DEPT_NAME="Not SupervisorDept", ACCOUNT="6740", ORG="2114", departmentCompliance = 1)

        # initialize students for testing
        inDeptStudent = Student.create(ID="B10701360", PIDM=3, FIRST_NAME="Tyler", LAST_NAME="Parton", CLASS_LEVEL="Senior", STU_EMAIL="partont@berea.edu")
        outDeptStudent = Student.create(ID="B00000000", PIDM=4, FIRST_NAME="Not", LAST_NAME="Tyler", CLASS_LEVEL="Not a Senior", STU_EMAIL="tylern@berea.edu")

        # intitialize supervisor for testing
        outOfDeptSuper = Supervisor.create(ID="B00000001", PIDM=75, FIRST_NAME="Not", LAST_NAME="Scott", EMAIL="None", CPO="None", DEPT_NAME="Biology")
        outOfDeptSuperUser = User.create(student=None, supervisor=outOfDeptSuper.ID, username="scottn", isLaborAdmin=None, isFinancialAidAdmin=None, isSaasAdmin=None)

        # intialize labor status forms
        inDeptForm = LaborStatusForm.create(StudentName="Tyler Parton", termCode=202000, studentSupervisee="B10701360", supervisor="B00763721", department=1, jobType="Primary", WLS="1", POSN_TITLE="Student Programmer", POSN_CODE="S61407")
        outDeptForm = LaborStatusForm.create(StudentName="Not Tyler", termCode=202000, studentSupervisee="B00000000", supervisor="B00000001", department=4, jobType="Primary", WLS="1", POSN_TITLE="Student Programmer", POSN_CODE="S61409")

        # intialize form history for testing
        inDeptFormHistory = FormHistory.create(formID=inDeptForm.laborStatusFormID, historyType="Labor Status Form", releaseForm=None, adjustedForm=None, overloadForm=None, createdBy=1, createdDate="2020-04-14", reviewedDate=None, reviewedBy=None, status="Approved")
        outDeptFormHistory = FormHistory.create(formID=outDeptForm.laborStatusFormID, historyType="Labor Status Form", releaseForm=None, adjustedForm=None, overloadForm=None, createdBy=outOfDeptSuperUser.userID, createdDate="2020-04-14", reviewedDate=None, reviewedBy=None, status="Approved")

        students = [inDeptStudent, outDeptStudent]
        students_converted = [studentDbToDict(student) for student in students]
        newStudents = limitSearch(students_converted, outOfDeptSuperUser)

        assert students_converted[1] not in newStudents
        assert students_converted[0] in newStudents

        transaction.rollback()
