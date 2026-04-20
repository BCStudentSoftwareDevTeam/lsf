from app.models.activePosition import *
from app.models.laborStatusForm import *
from app.models.department import * 
from app.models import mainDB
from app.models.Tracy.stuposn import STUPOSN
from app.logic.departmentPositions import updatePositionRecords

def populate_active_positions():
    with mainDB.transaction():
        activePositions = list(
            STUPOSN.query
                .with_entities( STUPOSN.DEPT_NAME, STUPOSN.POSN_CODE, func.min(STUPOSN.POSN_TITLE).label("POSN_TITLE"), func.min(STUPOSN.WLS).label("WLS"))
                .group_by(STUPOSN.DEPT_NAME, STUPOSN.POSN_CODE).order_by(STUPOSN.DEPT_NAME).all())
        updatePositionRecords()
        for position in activePositions:
            departmentID = Department.get_or_none(Department.DEPT_NAME == position[0])        
            ActivePosition.create(department = departmentID, POSN_TITLE = position[1], POSN_CODE = position[2], WLS = position[3])

if __name__ == "__main__":
    populate_active_positions()