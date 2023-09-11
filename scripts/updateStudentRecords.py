from app.logic.userInsertFunctions import updatePersonRecords


studentsUpdated, studentsFailed, supervisorsUpdated, supervisorsFailed = updatePersonRecords()
print("Students updated: " + str(studentsUpdated))
print("Students failed: " + str(studentsFailed))
print("Supervisors updated: " + str(supervisorsUpdated))
print("Supervisors failed: " + str(supervisorsFailed))
print("Total updates: " + str(studentsUpdated + supervisorsUpdated))
print("Total fails: " + str(studentsFailed + supervisorsFailed))
