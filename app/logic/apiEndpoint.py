from flask import jsonify
from app.config.loadConfig import*

from app.models.laborStatusForm import LaborStatusForm
from app.models.department import Department
from app.models.formHistory import FormHistory
from app.models.term import Term

def getLaborInformation(orgCode = "", bNumber = ""):
    #TODO: need to add tests. 

    if not orgCode:
        # The default right now is just to search within CELTS Departments, so setting it 
        # here if it is not passed in. 
        orgCode = 2084

    givenOrgCode = (Department.select(Department.departmentID)
                              .where(Department.ORG == orgCode))
    
    deptLabor = (LaborStatusForm.select(LaborStatusForm.studentSupervisee_id, 
                                        LaborStatusForm.termCode, 
                                        LaborStatusForm.POSN_TITLE,
                                        LaborStatusForm.startDate, 
                                        LaborStatusForm.endDate,  
                                        LaborStatusForm.jobType, 
                                        LaborStatusForm.WLS,
                                        )
                                .join(Term).switch(LaborStatusForm)
                                .join(FormHistory)
                                .where(LaborStatusForm.department_id.in_(givenOrgCode), 
                                       FormHistory.status_id == "Approved")
                                .order_by(LaborStatusForm.termCode_id))

    if bNumber: 
        deptLabor = deptLabor.where(LaborStatusForm.studentSupervisee_id == bNumber)        

    laborFormDict = {}
    for laborForm in deptLabor:
        if laborForm.studentSupervisee_id not in laborFormDict:
            laborFormDict[laborForm.studentSupervisee_id] = []
        laborFormDict[laborForm.studentSupervisee_id].append({"positionTitle": laborForm.POSN_TITLE, 
                                                              "termCode":laborForm.termCode_id, 
                                                              "laborStart":laborForm.startDate, 
                                                              "laborEnd":laborForm.endDate, 
                                                              "jobType":laborForm.jobType, 
                                                              "wls":laborForm.WLS,
                                                              "termName": laborForm.termCode.termName})

    return jsonify(laborFormDict)