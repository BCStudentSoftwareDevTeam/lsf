from app.models import *
from app.models.department import Department
from app.models.positionHistory import PositionHistory

# class ActivePosition(baseModel):
#     positions = ForeignKeyField(PositionHistory)
#     positions.insert_many(PositionHistory.active())

class ActivePosition(baseModel):
    positions = ForeignKeyField(PositionHistory)