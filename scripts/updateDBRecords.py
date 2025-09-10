from app.logic.userInsertFunctions import updatePersonRecords, updatePositionRecords


studentsFound, studentsNotFound, studentsFailed, supervisorsFound, supervisorsNotFound, supervisorsFailed = updatePersonRecords()
("Students updated: " + str(studentsFound))
("Students not found: " + str(studentsNotFound))
("Students failed: " + str(studentsFailed))
("Supervisors updated: " + str(supervisorsFound))
("Supervisors not found: " + str(supervisorsNotFound))
("Supervisors failed: " + str(supervisorsFailed))
("Total Person updates: " + str(studentsFound + supervisorsFound))
("Total Person fails: " + str(studentsFailed + supervisorsFailed))
departmentsPulledFromTracy, departmentsUpdated, departmentsNotFound, departmentsFailed = updatePositionRecords()
("New Departments pulled: " + str(departmentsPulledFromTracy))
("Departments updated: " + str(departmentsUpdated))
("Departments not found: " + str(departmentsNotFound))
("Departments failed: " + str(departmentsFailed))

