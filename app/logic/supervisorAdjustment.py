from app.models.supervisor import Supervisor
from app.models.department import Department
from app.logic.tracy import Tracy
from app.logic.userInsertFunctions import createSupervisorFromTracy


def checkAdjustment(allForms):
    """
        Retrieve supervisor and position information for adjusted forms using the new values
        stored in adjusted table and update allForms
    """
    if allForms.adjustedForm:

        if allForms.adjustedForm.fieldAdjusted == "supervisor":
            # use the supervisor id in the field adjusted to find supervisor in User table.
            newSupervisorID = allForms.adjustedForm.newValue
            newSupervisor = Supervisor.get(Supervisor.ID == newSupervisorID)
            if not newSupervisor:
                newSupervisor = createSupervisorFromTracy(bnumber=newSupervisorID)

            # we are temporarily storing the supervisor name in new value,
            # because we want to show the supervisor name in the hmtl template.
            allForms.adjustedForm.newValue = newSupervisor.FIRST_NAME +" "+ newSupervisor.LAST_NAME
            allForms.adjustedForm.oldValue = {"email":newSupervisor.EMAIL, "ID":newSupervisor.ID}

        if allForms.adjustedForm.fieldAdjusted == "position":
            newPositionCode = allForms.adjustedForm.newValue
            newPosition = Tracy().getPositionFromCode(newPositionCode)
            # temporarily storing the position code and wls in new value, and position name in old value
            # because we want to show these information in the hmtl template.
            allForms.adjustedForm.newValue = newPosition.POSN_CODE +" (" + newPosition.WLS+")"
            allForms.adjustedForm.oldValue = newPosition.POSN_TITLE

        if allForms.adjustedForm.fieldAdjusted == "department":
            newDepartment = Department.get(Department.ORG==allForms.adjustedForm.newValue)
            allForms.adjustedForm.newValue = newDepartment.DEPT_NAME
            allForms.adjustedForm.oldValue = newDepartment.ORG + "-" + newDepartment.ACCOUNT