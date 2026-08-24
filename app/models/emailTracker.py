from app.models import *
from app.models.laborStatusForm import LaborStatusForm
from app.models.emailTemplate import EmailTemplate

class EmailTracker(baseModel):
    emailTrackerID     = PrimaryKeyField()
    formID             = ForeignKeyField(LaborStatusForm)               # foreign key to lsf
    date               = DateField()
    recipient          = CharField()
    template           = ForeignKeyField(EmailTemplate)                 # foreign key to email template
    recipientEmails    = TextField()
    body               = TextField()
    
    
