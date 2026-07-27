from app.models.positionHistory import PositionHistory

def getActivePositions(dept):
    """
    Returns a list of active positions for a given department, along with their corresponding position codes.
    The function filters out duplicate position codes within the same department and ensures that a position code can only be Active in ONE place at a time.
    """
    if not dept:
        return [], []

    positions = list(PositionHistory.select()
                    .where(PositionHistory.department == dept, PositionHistory.status == "Active")
                    .order_by(PositionHistory.positionTitle.asc()))

    positionsList = []
    posURL = []
    seenPositionCodes = set()
    for pos in positions:
        positioncode = pos.positionCode

        if positioncode in seenPositionCodes:
            continue

        isPositionClaimed = (PositionHistory
                            .select()
                            .where(
                                PositionHistory.positionCode == positioncode,
                                PositionHistory.status == "Active",
                                PositionHistory.department != dept,
                                PositionHistory.id < pos.id
                            )
                            .exists())

        if isPositionClaimed:
            continue

        seenPositionCodes.add(positioncode)
        positionsList.append(pos.positionTitle + ": " + "(WLS " + str(pos.wls) + ")")
        posURL.append(str(pos.positionCode))

    return positionsList, posURL