from app.models.laborStatusForm import *
from app.models.formHistory import *
from peewee import fn


def getUsedBreakHours(terms):
    # totalBreakSum = FormHistory.select(fn.SUM(LaborStatusForm.contractHours)).where( (FormHistory.historyType_id == "Labor Status Form ") & (FormHistory.status_id == "Approved"))

    totalBreakSum = (
    FormHistory
    .select(
        LaborStatusForm.department,
        LaborStatusForm.termCode,
        fn.SUM(LaborStatusForm.contractHours).alias('totalHours')
        
    )
    .join(
        LaborStatusForm,
        on=(FormHistory.formID == LaborStatusForm.laborStatusFormID)
    )
    .where(
        (FormHistory.historyType == "Labor Status Form") &
        (FormHistory.status == "Approved") &
        # LaborStatusForm.termCode.in_(terms) # Should have a list of terms, not just one term.
    )
    .group_by(LaborStatusForm.department, LaborStatusForm.termCode).dicts()
)
    # correctLSF = LaborStatusForm.select().where(LaborStatusForm.termCode == term)

    # print("Something2\n\n\n\n",list(correctLSF))

    return totalBreakSum

# def getCurrentSelectedTerm(currentTerm):
    #'''
    #Returns the current term code based on a the selected term from a dropdown menu in the manage departments page.
    #Should only contain the current term, the next term, and the previous term.
    #'''
    