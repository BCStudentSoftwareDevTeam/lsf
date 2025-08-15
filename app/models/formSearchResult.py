from datetime import datetime

from app.models import *
from app.models.user import User


class FormSearchResult(baseModel):
    name        = CharField()
    formHistoryIds     = TextField() # holds a json list of FormHistory IDs
    searchType  = CharField() # key that CSVMaker uses to determine fields
    generatedBy = ForeignKeyField(User)
    generatedOn = DateTimeField(default=datetime.now)
