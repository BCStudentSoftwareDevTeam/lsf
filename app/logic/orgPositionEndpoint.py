from flask import jsonify
from app.config.loadConfig import*
from app import app

from app.models.laborStatusForm import LaborStatusForm
from app.models.department import Department
from app.models.formHistory import FormHistory

def getFormsForOrg(orgCode):
    '''
    Returns relevant labor information for CELTS labor students to be sent to CELTS-Link
    '''
    # TODO: Write test 

    givenOrgCode = (Department.select(Department.departmentID)
                              .where(Department.ORG == orgCode))

    deptLabor = (LaborStatusForm.select(LaborStatusForm.studentSupervisee_id, 
                                        LaborStatusForm.termCode_id, 
                                        LaborStatusForm.POSN_TITLE,
                                        LaborStatusForm.startDate, 
                                        LaborStatusForm.endDate,  
                                        LaborStatusForm.jobType, 
                                        LaborStatusForm.WLS)
                                .join(FormHistory)
                                .where(LaborStatusForm.department_id.in_(givenOrgCode), 
                                       FormHistory.status_id == "Approved")
                                .order_by(LaborStatusForm.termCode_id))        
    
    laborFormDict = {}
    for laborForm in deptLabor:
        if laborForm.studentSupervisee_id not in laborFormDict:
            laborFormDict[laborForm.studentSupervisee_id] = []
        laborFormDict[laborForm.studentSupervisee_id].append({"termCode":laborForm.termCode_id, 
                                                              "laborStart":laborForm.startDate, 
                                                              "laborEnd":laborForm.endDate, 
                                                              "positionTitle": laborForm.POSN_TITLE, 
                                                              "jobType":laborForm.jobType, 
                                                              "wls":laborForm.WLS})

    return jsonify(laborFormDict)