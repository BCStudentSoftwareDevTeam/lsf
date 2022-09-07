import pytest
from app.models import mainDB
from app.models.department import Department
from app.models.student import Student
from app.models.supervisor import Supervisor
from app.models.laborStatusForm import LaborStatusForm
from app.models.formHistory import FormHistory
from peewee import DoesNotExist
from app.logic.search import limitSearch

@pytest.mark.integration
def test_search():
    with mainDB.atomic() as transaction:
        supervisorDept = Department.create(DEPT_NAME="supervisorDept", ACCOUNT="6740", ORG="2114", departmentCompliance = 1)
        unattachedDept = Department.create(DEPT_NAME="Not SupervisorDept", ACCOUNT="6740", ORG="2114", departmentCompliance = 1)
        inDeptStudent = Student.create(ID="B00751360", PIDM="3", FIRST_NAME="Tyler", LAST_NAME="Parton", CLASS_LEVEl="Senior")
        inDeptStudent = Student.create(ID="B00000000", PIDM="3", FIRST_NAME="Not", LAST_NAME="Tyler", CLASS_LEVEl="Not a Senior")
        outOfDeptSuper = Supervisor.create(ID="B00000001", PIDM=75, FIRST_NAME="Not", LAST_NAME="Scott", EMAIL="None", CPO="None", DEPT_NAME="Biology")
        inDeptForm = LaborStatusForm.create(StudentName="Tyler Parton", termCode=202000, studentSupervisee="B00751360", supervisor="B00763721", department=1, jobType="Primary", WLS="1", POSN_TITLE="Student Programmer", POSN_CODE="S61407")
        outDeptForm = LaborStatusForm.create(StudentName="Not Tyler", termCode=202000, studentSupervisee="B00000000", supervisor="B00000001", department=4, jobType="Primary", WLS="1", POSN_TITLE="Student Programmer", POSN_CODE="S61409")
        inDeptFormHistory = FormHistory.create(formID=inDeptForm.laborStatusFormID, historyType="Labor Status Form", releaseForm=None, adjustedForm=None, overloadForm=None, createdBy=1, createdDate="2020-04-14", reviewedDate=None, reviewedBy=None, status="Approved")
        inDeptFormHistory = FormHistory.create(formID=outDeptForm.laborStatusFormID, historyType="Labor Status Form", releaseForm=None, adjustedForm=None, overloadForm=None, createdBy=outOfDeptSuper.ID, createdDate="2020-04-14", reviewedDate=None, reviewedBy=None, status="Approved")

        assert inDeptFormHistory
        transaction.rollback()
