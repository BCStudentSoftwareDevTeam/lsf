import pytest
from app.models import mainDB
from app.logic.getSupervisors import *
from app.models.supervisor import Supervisor
from app.models.supervisorDepartment import SupervisorDepartment
from app.models.department import Department

@pytest.mark.integration
def test_getSupervisors():
    with mainDB.atomic() as transaction:
        dept = Department.create(departmentID = 10000,
                                 DEPT_NAME = "Test Computer Science",
                                 ACCOUNT = "4",
                                 ORG = "1",
                                 departmentCoimpliance = 1,
                                 isActive = 1)
        
        staff = Supervisor.create(ID = "B0000000",
                                  PIDM = 10000,
                                  LAST_NAME = "Subject",
                                  legal_name = "Test",
                                  EMAIL = "test@berea.edu",
                                  CPO = "9000",
                                  ORG = "1",
                                  DEPT_NAME = "Test Computer Science")
        staff2 = Supervisor.create(ID = "B2000000",
                                  PIDM = 1002,
                                  LAST_NAME = "Extra",
                                  legal_name = "Tester",
                                  EMAIL = "Extra@berea.edu",
                                  CPO = "9002",
                                  ORG = "1",
                                  DEPT_NAME = "Test Computer Science")

        testCoordinator = Supervisor.create(ID = "B10000000",
                                      PIDM = 10000,
                                      LAST_NAME = "Coordinator",
                                      legal_name = "Labor",
                                      EMAIL = "Coordinator@berea.edu",
                                      CPO = "9001",
                                      ORG = "1",
                                      DEPT_NAME = "Test Computer Science")
            
        SupervisorDepartment.create(supervisor = "B0000000",
                                    department = 10000,
                                    isCoordinator = 0)
        SupervisorDepartment.create(supervisor = "B10000000",
                                    department = 10000,
                                    isCoordinator = 1)
        SupervisorDepartment.create(supervisor = "B2000000",
                                    department = 10000,
                                    isCoordinator = 0)

        checkDept = getSupervisors(dept)
        #checks whether not the supervisors Names are in the correct list, [supervisors, coordinators]
        #The checkDept returns a tuple(Supervisor, Coordinator) with a list with dictionaries with the information about each person.
        #The checkDept return is in order by LAST_NAME
        assert "Subject" == checkDept[0][1]['name'].split(' ')[1]
        assert"Subject" != checkDept[1][0]['name'].split(' ')[1]
        assert "Coordinator" == checkDept[1][0]['name'].split(' ')[1]
        assert "Extra" == checkDept[0][0]['name'].split(' ')[1]

        transaction.rollback()
 