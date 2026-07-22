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
    seenCodes = set()
    # Iterate through the positions and filter out duplicates based on positionCode and department
    for pos in positions:
        code = pos.positionCode

        # Same dept returned two Active rows with the same code (shouldn't normally happen, but guards against bad data) -> skip the duplicate
        if code in seenCodes:
            continue

        # Enforces: A positionCode can only be Active in ONE place at a time, regardless of department or revisionDate. 
        # If an earlier-created Active row with this code exists in a DIFFERENT department, this one loses.
        claimedElsewhere = (PositionHistory
                            .select()
                            .where(
                                PositionHistory.positionCode == code,
                                PositionHistory.status == "Active",
                                PositionHistory.department != dept,
                                PositionHistory.id < pos.id # Uses PeeWee's auto-incrementing ID to determine which row was created first.
                            )
                            .exists())

        if claimedElsewhere:
            continue

        seenCodes.add(code) # Mark this code as seen for the current department to avoid duplicates
        positionsList.append(pos.positionTitle + ": " + "(WLS " + str(pos.wls) + ")")
        posURL.append(str(pos.positionCode))

    return positionsList, posURL