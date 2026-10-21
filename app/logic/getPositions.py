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

def getPositions(dept):
    return((PositionHistory.select()
                                .where((PositionHistory.department == dept) &
                                       (PositionHistory.status == "Active"))
                                .order_by(PositionHistory.positionTitle.asc())))

def getPositionsPendingReview(department):
    """
    Returns the active positions in a department that haven't had an Annual
    Position Review requested yet.
    """
    return list(PositionHistory.select()
                .where(PositionHistory.department == department,
                       PositionHistory.status == "Active",
                       PositionHistory.reviewRequested == False))

def markPositionsReviewRequested(positions):
    """
    Records that an Annual Position Review was requested for the given positions.
    """
    return (PositionHistory
            .update(reviewRequested=True)
            .where(PositionHistory.id.in_([position.id for position in positions]))
            .execute())

def getPositionDescriptionSections(position):
    """
    Returns the description sections for a given position, ordered for display.
    """
    positionDescriptionSections = list(PositionDescriptionSection.select()
                                       .where(PositionDescriptionSection.position == position)
                                       .order_by(PositionDescriptionSection.order.asc()))
    
    return positionDescriptionSections


