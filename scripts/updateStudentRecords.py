from app.logic.userInsertFunctions import updatePersonRecords, updatePositionRecords


studentsUpdated, studentsFailed, supervisorsUpdated, supervisorsFailed = updatePersonRecords()
print("Students updated: " + str(studentsUpdated))
print("Students failed: " + str(studentsFailed))
print("Supervisors updated: " + str(supervisorsUpdated))
print("Supervisors failed: " + str(supervisorsFailed))
print("Total Person updates: " + str(studentsUpdated + supervisorsUpdated))
print("Total Person fails: " + str(studentsFailed + supervisorsFailed))
departmentsUpdated, departmentsFailed = updatePositionRecords()
print("Departments updated: " + str(departmentsUpdated))
print("Departments failed: " + str(departmentsFailed))

