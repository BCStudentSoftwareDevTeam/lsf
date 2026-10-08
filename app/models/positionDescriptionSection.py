from app.models import *
from app.models.positionHistory import PositionHistory


class PositionDescriptionSection (baseModel):
    position                        = ForeignKeyField(PositionHistory)
    sectionTitle                    = CharField()
    sectionContent                  = TextField()
    order                           = IntegerField() # Order of the sections in the position description



