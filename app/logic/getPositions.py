from app.models.positionHistory import PositionHistory
from app.models.positionDescriptionSection import PositionDescriptionSection

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

def getPosition(dept, positionCode, revisionDate=None):
    """
    Returns a single position for a given department, position code, and optional revision date. 
    If no revision date is provided, the most recent revision is returned.
    """
    positionQuery = PositionHistory.select().where(
        PositionHistory.department == dept,
        PositionHistory.positionCode == positionCode
    )

    if revisionDate:
        positionQuery = positionQuery.where(PositionHistory.revisionDate == revisionDate)

    return positionQuery.order_by(PositionHistory.revisionDate.desc()).first()

def getPositionDescriptionSections(position):
    """
    Returns the description sections for a given position, ordered for display.
    """
    positionDescriptionSections = list(PositionDescriptionSection.select()
                                       .where(PositionDescriptionSection.position == position)
                                       .order_by(PositionDescriptionSection.order.asc()))
    
    return positionDescriptionSections

