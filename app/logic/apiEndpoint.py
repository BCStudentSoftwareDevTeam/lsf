from flask import jsonify
from datetime import datetime
from app.config.loadConfig import*
from collections import defaultdict

from app.models.laborStatusForm import LaborStatusForm
from app.models.department import Department
from app.models.formHistory import FormHistory
from app.models.term import Term

def getLaborInformation(*, orgCode = "2084", bNumber = ""):
    """
    input: organization code or bNumber of a student  

    orgCode is set to 2084 since that is the CELTS org code and there are no plans 
    currently to use the endpoint for any org other than CELTS. 

    output: jsonified default dict containt either a whole departments labor information or a specific 
    students labor history.
    """

    orgDepartmentCode = (Department.select(Department.departmentID)
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
                                .where(LaborStatusForm.department_id.in_(orgDepartmentCode), 
                                       FormHistory.status_id == "Approved", 
                                       FormHistory.historyType_id == "Labor Status Form")
                                .order_by(LaborStatusForm.termCode_id))
    if bNumber: 
        deptLabor = deptLabor.where(LaborStatusForm.studentSupervisee_id == bNumber)       

    laborFormDict = defaultdict(list)
    for laborForm in deptLabor:
        laborFormDict[laborForm.studentSupervisee_id].append({"positionTitle": laborForm.POSN_TITLE,
                                                              "termCode": laborForm.termCode_id,
                                                              "laborStart": datetime.strftime(laborForm.startDate, "%Y-%m-%d"),
                                                              "laborEnd": datetime.strftime(laborForm.endDate, "%Y-%m-%d"),
                                                              "jobType": laborForm.jobType,
                                                              "wls": laborForm.WLS,
                                                              "termName": laborForm.termCode.termName
                                                            })
    return jsonify(laborFormDict)