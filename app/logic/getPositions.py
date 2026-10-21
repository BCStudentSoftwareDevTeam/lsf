from app.models.positionHistory import PositionHistory
from app.models.positionDescriptionSection import PositionDescriptionSection
from peewee import fn

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

def getPositions(dept):
    """
    Returns a single position for a given department, position code, and optional revision date and status. If no revision date is provided, the most recent revision is returned.
    """
    positionQuery = PositionHistory.select().where(
        PositionHistory.department == dept,
        PositionHistory.positionCode == positionCode
    )

    if revisionDate:
        positionQuery = positionQuery.where(PositionHistory.revisionDate == revisionDate)

    if status:
        positionQuery = positionQuery.where(PositionHistory.status == status)

    return positionQuery.order_by(PositionHistory.revisionDate.desc()).first()

def getPositionDescriptionSections(position):
    """
    Returns the description sections for a given position, ordered for display.
    """
    positionDescriptionSections = list(PositionDescriptionSection.select()
                                       .where(PositionDescriptionSection.position == position)
                                       .order_by(PositionDescriptionSection.order.asc()))
    
    return positionDescriptionSections




def getToBeReviewedPosition(dept):
    
    """
    This query first checks with the position history table and creates a copy
    filtres out the ones that have active position

    the second query checks the oens that have requested on and also the position code existes in has active that way we filter out the ones that have active position and now are requeted fro revision.
    """

    ActiveRow = PositionHistory.alias()

    has_active = (ActiveRow
                .select()
                .where((ActiveRow.positionCode == PositionHistory.positionCode) &
                        (ActiveRow.status == "Active")))

    requested = (PositionHistory
                .select()
                .where((PositionHistory.department == dept) &
                        (PositionHistory.status == "Requested") &
                        fn.EXISTS(has_active)))
    

    return requested


def getRequestedPosition(dept,poscode):

    positionToBeReviewd = getToBeReviewedPosition(dept).select().where(PositionHistory.positionCode == poscode).first()
    
    return positionToBeReviewd


# so  for next time remember thism, the data for preivou position and new position is the same and previous is takign from requested for some reason figure that out and get the description.