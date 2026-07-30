from app.models.positionHistory import PositionHistory

def getActivePositions(dept):
    """
    Returns a list of active positions for a given department.
    """

    positions = list(PositionHistory.select()
                    .where(PositionHistory.department == dept, PositionHistory.status == "Active")
                    .order_by(PositionHistory.positionTitle.asc())) if dept else []

    positionsList = []
    posURL = []
    if positions == []:
        pass    
    else:
        for i in positions:
            positionsList.append(i.positionTitle + ": " + "(WLS " + str(i.wls) + ")")
            posURL.append(str(i.positionCode))

    return positionsList, posURL

def supervisorsPositions(dept):
    return((PositionHistory.select()
                                .where((PositionHistory.department == dept) &
                                       (PositionHistory.status == "Active"))
                                .order_by(PositionHistory.positionTitle.asc())))