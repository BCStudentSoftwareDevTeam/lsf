from app.logic.tracy import Tracy, InvalidQueryException
from app.models.department import Department
from app.models.Tracy.stuposn import STUPOSN


def updatePositionRecords():
    remoteDepartments = Tracy().getDepartments()  # Create local copies of new departments in Tracy
    departmentsPulledFromTracy = 0
    for dept in remoteDepartments:
        d = Department.get_or_none(ACCOUNT=dept.ACCOUNT, ORG=dept.ORG)
        if d:
            d.DEPT_NAME = dept.DEPT_NAME
            d.save()
        else:
            Department.create(DEPT_NAME=dept.DEPT_NAME, ACCOUNT=dept.ACCOUNT, ORG=dept.ORG)
            departmentsPulledFromTracy += 1

    departmentsInDB = list(Department.select())
    departmentsUpdated = 0
    departmentsNotFound = 0
    departmentsFailed = 0
    for department in departmentsInDB:
        try:
            updateDepartmentRecord(department)
            departmentsUpdated += 1
        except InvalidQueryException as e:
            departmentsNotFound += 1
        except Exception as e:
            departmentsFailed += 1

    return departmentsPulledFromTracy, departmentsUpdated, departmentsNotFound, departmentsFailed

def updateDepartmentRecord(department):
    tracyDepartment = STUPOSN.query.filter((STUPOSN.ORG == department.ORG) & (STUPOSN.ACCOUNT == department.ACCOUNT)).first()

    department.isActive = bool(tracyDepartment)
    if tracyDepartment is None:
        raise InvalidQueryException("Department ({department.ORG}, {department.ACCOUNT}) not found")
        
    
    department.DEPT_NAME = tracyDepartment.DEPT_NAME
    department.save()
