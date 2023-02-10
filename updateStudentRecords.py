from app.logic.userInsertFunctions import updateDBRecords

studentsUpdated, studentsFailed, supervisorsUpdated, supervisorsFailed = updateDBRecords()
print("Students updated: " + str(studentsUpdated))
print("Students failed: " + str(studentsFailed))
print("Supervisors updated: " + str(supervisorsUpdated))
print("Supervisors failed: " + str(supervisorsFailed))
print("Total updates: " + str(studentsUpdated + supervisorsUpdated))
print("Total fails: " + str(studentsFailed + supervisorsFailed))
