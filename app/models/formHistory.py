from app.models import *
from app.models.laborStatusForm import LaborStatusForm
from app.models.laborReleaseForm import LaborReleaseForm
from app.models.adjustedForm import AdjustedForm
from app.models.overloadForm import OverloadForm
from app.models.status import Status
from app.models.user import User
from app.models.historyType import HistoryType
from app.models.supervisor import Supervisor

class FormHistory(baseModel):
    formHistoryID       = PrimaryKeyField()
    formID              = ForeignKeyField(LaborStatusForm, on_delete="cascade")               # foreign key to lsf
    # overloadID          = ForeignKeyField(OverloadForm, on_delete = "cascade")
    historyType         = ForeignKeyField(HistoryType)                                        # foreign key to historytype
    releaseForm         = ForeignKeyField(LaborReleaseForm, null=True, on_delete="cascade")  # if its a release form
    adjustedForm        = ForeignKeyField(AdjustedForm, null=True,on_delete="cascade")      # if its a form modification
    overloadForm        = ForeignKeyField(OverloadForm, null=True, on_delete="cascade")      # if its an overload application
    createdBy           = ForeignKeyField(User, related_name="creator",  on_delete="cascade") # Foreign key to USERS
    createdDate         = DateField()
    reviewedDate        = DateField(null=True)
    reviewedBy          = ForeignKeyField(User, null=True, related_name="reviewer",  on_delete="SET NULL") # Foreign key to Supervisor
    status              = ForeignKeyField(Status)                       # Foreign key to Status # Approved, Denied, Pending
    rejectReason        = TextField(null=True)                          # This should not be null IF that status is rejected

    
    def __str__(self):
        return str(self.__dict__)
    
    @staticmethod
    def order_by_term(query, reverse=False):
        """
        Accepts the results of a query where each object has had a `termCode` column selected.
        Sorts by the Term Code in logical order based first on year and then by the seasonalCode
        
        seasonalCode := last two digits of the term code which maps arbitrarily to the name of the term, break, etc.
        """
        termCodeOrders = ((0, 0), ("Default", 1), (11, 2), (4, 3), (1, 4), (2, 5), (12, 6), (5, 7), (3, 8), (13, 9))
        termCode = FormHistory.formID.termCode
        yearColumn = fn.substring(termCode.cast("char"), 1, 4)
        seasonalColumn = fn.substring(termCode.cast("char"), 5, 6)
        orderValues = Case(seasonalColumn, termCodeOrders, 1)
        return (query
                    #  .select(FormHistory, 
                    #          seasonalColumn.alias('seasonalCode'), 
                    #          yearColumn.alias('yearCode'), 
                    #          orderValues.alias('orderValue'))
                     #.join(LaborStatusForm, JOIN.LEFT_OUTER, on=(FormHistory.formID == LaborStatusForm.laborStatusFormID))
                     .order_by(yearColumn.desc() if reverse else yearColumn, 
                               orderValues.desc() if reverse else orderValues))


