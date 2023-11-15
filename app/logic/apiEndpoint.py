from flask import jsonify
from datetime import datetime
from app.config.loadConfig import*

from app.models.laborStatusForm import LaborStatusForm
from app.models.department import Department
from app.models.formHistory import FormHistory
from app.models.term import Term

def getLaborInformation(orgCode = "", bNumber = ""):

    if not orgCode:
        # The default right now is just to search within CELTS Departments, so setting it 
        # here if it is not passed in. 
        orgCode = 2084

    givenOrgCode = (Department.select(Department.departmentID)
                              .where(Department.ORG == orgCode))
    
    deptLabor = (LaborStatusForm.select(LaborStatusForm.studentSupervisee, 
                                        LaborStatusForm.termCode, 
                                        LaborStatusForm.POSN_TITLE,
                                        LaborStatusForm.startDate, 
                                        LaborStatusForm.endDate,  
                                        LaborStatusForm.jobType, 
                                        LaborStatusForm.WLS,
                                        Term
                                        )
                                .join(Term).switch(LaborStatusForm)
                                .join(FormHistory)
                                .where(LaborStatusForm.department_id.in_(givenOrgCode), 
                                       FormHistory.status_id == "Approved", 
                                       FormHistory.historyType_id == "Labor Status Form")
                                .order_by(LaborStatusForm.termCode_id))
    if bNumber: 
        deptLabor = deptLabor.where(LaborStatusForm.studentSupervisee_id == bNumber)        
    laborFormDict = {}
    for laborForm in deptLabor:
        if laborForm.studentSupervisee_id not in laborFormDict:
            laborFormDict[laborForm.studentSupervisee_id] = []
        laborFormDict[laborForm.studentSupervisee_id].append({"positionTitle": laborForm.POSN_TITLE, 
                                                              "termCode":laborForm.termCode_id, 
                                                              "laborStart":datetime.strftime(laborForm.startDate, "%Y-%m-%d"), 
                                                              "laborEnd":datetime.strftime(laborForm.endDate, "%Y-%m-%d") , 
                                                              "jobType":laborForm.jobType, 
                                                              "wls":laborForm.WLS,
                                                              "termName": laborForm.termCode.termName})
    return jsonify(laborFormDict)