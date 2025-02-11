from app.logic.userInsertFunctions import updatePersonRecords, updatePositionRecords


studentsFound, studentsNotFound, studentsFailed, supervisorsFound, supervisorsNotFound, supervisorsFailed = updatePersonRecords()
print("Students updated: " + str(studentsFound))
print("Students not found: " + str(studentsNotFound))
print("Students failed: " + str(studentsFailed))
print("Supervisors updated: " + str(supervisorsFound))
print("Supervisors not found: " + str(supervisorsNotFound))
print("Supervisors failed: " + str(supervisorsFailed))
print("Total Person updates: " + str(studentsFound + supervisorsFound))
print("Total Person fails: " + str(studentsFailed + supervisorsFailed))
departmentsPulledFromTracy, departmentsUpdated, departmentsNotFound, departmentsFailed = updatePositionRecords()
print("New Departments pulled: " + str(departmentsPulledFromTracy))
print("Departments updated: " + str(departmentsUpdated))
print("Departments not found: " + str(departmentsNotFound))
print("Departments failed: " + str(departmentsFailed))

