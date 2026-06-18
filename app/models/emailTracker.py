from app.models import *
from app.models.laborStatusForm import LaborStatusForm

class EmailTracker(baseModel):
    emailTrackerID     = PrimaryKeyField()
    formID             = ForeignKeyField(LaborStatusForm, on_delete="cascade")               # foreign key to lsf
    date               = DateField()
    recipient          = CharField()
    subject            = CharField()
    body               = TextField()
    # template           = TextField()
    
