import pytest
from datetime import date, datetime
from app.logic.userInsertFunctions import *

@pytest.mark.integration
def testCreateLaborStatusForm():
    lsfDict = {
    "stuJobType":"Primary",
    "stuWLS":"1",
    "stuPosition":"Student Programmer",
    "stuPositionCode":"S61407",
    "stuContractHours":60,
    "stuWeeklyHours":20,
    "stuNotes":"new notes.",
    "stuLaborNotes":None,
    "stuName":"Elaheh Jamali",
    'stuStartDate': "04/01/2020",
    'stuEndDate': "09/01/2020"
    }

    createLaborStatusForm("B00730361", "B12365892", 1, 202000, lsfDict )
    currentUser = User.get(User.userID == 1)
    lsf = LaborStatusForm.get(LaborStatusForm.laborStatusFormID == 3)
    assert lsf.termCode_id == 202000
    assert lsf.studentSupervisee_id == "B00730361"
    assert lsf.supervisor_id == "B12365892"
    assert lsf.department_id == 1
    assert lsf.jobType == "Primary"
    assert lsf.WLS == "1"
    assert lsf.POSN_TITLE == "Student Programmer"
    assert lsf.POSN_CODE == "S61407"
    assert lsf.contractHours == 60
    assert lsf.weeklyHours == 20
    assert lsf.startDate == datetime.strptime("04/01/2020", "%m/%d/%Y").date()
    assert lsf.endDate == datetime.strptime("09/01/2020", "%m/%d/%Y").date()
    assert lsf.supervisorNotes == "new notes."
    assert lsf.laborDepartmentNotes == None
    assert lsf.studentName == "Elaheh Jamali"
