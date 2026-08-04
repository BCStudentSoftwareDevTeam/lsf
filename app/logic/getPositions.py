from app.models.positionHistory import PositionHistory
from app.models.positionDescriptionSection import PositionDescriptionSection
from datetime import date

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

def getPositionDescriptionSections(position):
    """
    Returns the description sections for a given position, ordered for display.
    """
    positionDescriptionSections = list(PositionDescriptionSection.select()
                                       .where(PositionDescriptionSection.position == position)
                                       .order_by(PositionDescriptionSection.order.asc()))

    return positionDescriptionSections

def createPositionRevision(position, revisedBy, positionTitle, wls, sectionTitles, sectionContents):
    """
    Creates a new pending (Requested) revision of a position, copying forward its
    department and position code, and replaces its description sections with the
    given titles/contents. Returns the newly created PositionHistory row.
    """
    newPosition = PositionHistory.create(
        positionTitle=positionTitle,
        positionCode=position.positionCode,
        department=position.department,
        status="Requested",
        wls=wls,
        revisionDate=date.today(),
        revisedBy=revisedBy
    )

    for order, (sectionTitle, sectionContent) in enumerate(zip(sectionTitles, sectionContents)):
        PositionDescriptionSection.create(
            position=newPosition,
            sectionTitle=sectionTitle,
            sectionContent=sectionContent,
            order=order
        )

    return newPosition

