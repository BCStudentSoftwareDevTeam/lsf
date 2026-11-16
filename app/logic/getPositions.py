from datetime import date
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

def getPositions(dept):
    """
    Returns a list of all positions for a given department, ordered by position title.
    """
    return((PositionHistory.select()
                                .where((PositionHistory.department == dept) &
                                       (PositionHistory.status == "Active"))
                                .order_by(PositionHistory.positionTitle.asc())))

# Labor Office policy: a position is due for review once it's gone this long without a revision.
POSITION_REVIEW_INTERVAL_YEARS = 5

def getPositionReviewCutoff(today=None):
    """
    Returns the date a position's revisionDate must be on or before to be due for review.
    """
    today = today or date.today()
    try:
        return today.replace(year=today.year - POSITION_REVIEW_INTERVAL_YEARS)
    except ValueError:
        # Feb 29 in a year whose counterpart isn't a leap year
        return today.replace(year=today.year - POSITION_REVIEW_INTERVAL_YEARS, day=28)

def getPositionsPendingReview(department):
    """
    Returns the active positions in a department that are due for a Position
    Review: not revised in the last POSITION_REVIEW_INTERVAL_YEARS years (or never
    given a revisionDate), and not already sent a review request.

    A revision creates a new PositionHistory row with a fresh revisionDate and
    reviewRequested unset, so a revised position isn't due again for another
    POSITION_REVIEW_INTERVAL_YEARS years.
    """
    return list(PositionHistory.select()
                .where(PositionHistory.department == department,
                       PositionHistory.status == "Active",
                       PositionHistory.reviewRequested == False,
                       (PositionHistory.revisionDate.is_null()) | (PositionHistory.revisionDate <= getPositionReviewCutoff())))

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


