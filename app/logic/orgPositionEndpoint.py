from flask import jsonify
from app.config.loadConfig import*
from app import app

from app.models.laborStatusForm import LaborStatusForm
from app.models.department import Department

def getPositionInfo(orgCode):
    '''
    Returns relevant labor information for CELTS labor students to be sent to CELTS-Link
    '''
    # TODO: Write test 

    givenOrgCode = (Department.select(Department.departmentID)
                              .where(Department.ORG == orgCode))
    laborFormDict = {}
    for deptCode in givenOrgCode:
        deptLabor = (LaborStatusForm.select(LaborStatusForm.studentSupervisee_id, LaborStatusForm.termCode_id,  LaborStatusForm.jobType, LaborStatusForm.WLS, LaborStatusForm.POSN_TITLE)
                                    .where(LaborStatusForm.department_id == deptCode))
        
        for laborForm in deptLabor:
            if laborForm.studentSupervisee_id not in laborFormDict:
                laborFormDict[laborForm.studentSupervisee_id] = []
            laborFormDict[laborForm.studentSupervisee_id].append((laborForm.termCode_id, laborForm.POSN_TITLE, laborForm.jobType, laborForm.WLS))

    return jsonify(laborFormDict)