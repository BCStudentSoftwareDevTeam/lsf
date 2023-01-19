from app.logic.userInsertFunctions import updateStudentDBRecords

def runUpdateFunction():
    attemptrun = updateStudentDBRecords()
    print(attemptrun)
    return True
