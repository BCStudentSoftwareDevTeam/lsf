#lsf File
from app.models import *
from app.models.user import User
from app.models.status import Status
from app.models.user import User

class OverloadForm(baseModel):
    overloadFormID          = PrimaryKeyField()
    studentOverloadReason   = CharField(null=True)
    financialAidApproved    = ForeignKeyField(Status, null=True, on_delete="cascade") #Foreign key to status
    financialAidApprover    = ForeignKeyField(User, null=True, on_delete="cascade")#Foreign key to Supervisor
    financialAidInitials    = CharField(null=True)
    financialAidReviewDate  = DateField(null=True)
    SAASApproved            = ForeignKeyField(Status, null=True, on_delete="cascade") #Foreign key to status
    SAASApprover            = ForeignKeyField(User, null=True, on_delete="cascade")#Foreign key to Supervisor
    SAASInitials            = CharField(null=True)
    SAASReviewDate          = DateField(null=True)
    laborApproved           = ForeignKeyField(Status, null=True, on_delete="cascade") #Foreign key to status
    laborApprover           = ForeignKeyField(User, null=True, on_delete="cascade")#Foreign key to Supervisor
    laborReviewDate         = DateField(null=True)
