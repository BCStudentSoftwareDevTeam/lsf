from app.logic.userInsertFunctions import updateDBRecords

studentsUpdated, studentsFailed, supervisorsUpdated, supervisorsFailed, departmentsUpdated, departmentsFailed = updateDBRecords()
print("Students updated: " + str(studentsUpdated))
print("Students failed: " + str(studentsFailed))
print("Supervisors updated: " + str(supervisorsUpdated))
print("Supervisors failed: " + str(supervisorsFailed))
print("Departments Updated: " + str(departmentsUpdated))
print("Departments Failed: " + str(departmentsFailed))
print("Total updates: " + str(studentsUpdated + supervisorsUpdated  + departmentsUpdated))
print("Total fails: " + str(studentsFailed + supervisorsFailed + departmentsFailed))
