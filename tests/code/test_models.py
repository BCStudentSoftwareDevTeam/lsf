import pytest
from app.models.user import User
from app.models.formHistory import FormHistory
from app.models.laborStatusForm import LaborStatusForm
from app.models.student import Student
from app.models.department import Department
from datetime import date, timedelta

from app.models.term import Term
from app.models import mainDB
from peewee import DoesNotExist, JOIN

for dept in Department.select().where(Department.isActive == True):
    print(dept.departmentID, dept.DEPT_NAME)

@pytest.mark.integration
def test_user_model():
    with mainDB.atomic() as transaction:
        sup_user = User.get(username="heggens")
        stu_user = User.get(username="jamalie")
        both_user = User.get(username="bryantal")

        assert sup_user.firstName == "Scott"
        assert sup_user.lastName == "Heggen"
        assert sup_user.fullName == "Scott Heggen"
        assert sup_user.email == "heggens@berea.edu"

        assert stu_user.firstName == "Elaheh"
        assert stu_user.lastName == "Jamali"
        assert stu_user.fullName == "Elaheh Jamali"
        assert stu_user.email == "jamalie@berea.edu"

        assert both_user.firstName == "Alex"
        assert both_user.lastName == "Bryant"
        assert both_user.fullName == "Alex Bryant"
        assert both_user.email == "bryantal@berea.edu"



        dept = Department.create(DEPT_NAME="Labor Department", isActive=True) #tests stu_user1 is Labor Student Staff & tests if LSF exists but not within current date
        inactive_dept = Department.create(DEPT_NAME="CS Department", isActive=False) #checks if stu_user2 isn't Labor Dep Student Worker if the dep isn't active 
        non_active_lab_dep = Department.create(DEPT_NAME="Labor Department", isActive=False) #checks if stu_user3 isn't a Labor Dep Student Worker if the Dep isn't active
        active_dept = Department.create(DEPT_NAME="CS Department", isActive=True) #checks if stu_user4 isn't Labor Dep Student Worker if the dep is Active
        case_sensive_name = Department.create(DEPT_NAME="labor department", isActive=True) #checking the case sensitiveness of the department name.
        case_sensive_name2 = Department.create(DEPT_NAME="labour dep", isActive=True) #checking the spelling sensetivity of the department name.

        student1 = Student.get(ID="B12345773")
        student2 = Student.get(ID="B12345783")
        student3 = Student.get(ID="B12345784")
        student4 = Student.get(ID="B12345785")
        student5 = Student.get(ID="B12345786") 
        student6 = Student.get(ID="B12345787") #multiple valid students working in the Active Labor Dep
        student7 = Student.get(ID="B12345788")
        student8 = Student.get(ID="B12345789")


        stu_user1 = User.create(username="tester",student=student1)
        stu_user2 = User.create(username="inactiveUser", student=student2)
        stu_user3 = User.create(username="inactiveDepartment", student=student3)
        stu_user4 = User.create(username="activeDepartment", student=student4)
        stu_user5 = User.create(username="inActiveTime", student=student5)
        user_non_stu = User.create(username="notStudent") #No student relation
        stu_user6 = User.create(username="tester2", student=student6)
        stu_user7 = User.create(username="casesense", student=student7)
        stu_user8 = User.create(username="casesense2", student=student8)


        LaborStatusForm.create(
            studentSupervisee=student1,
            department=dept,
            termCode_id="202000",
            supervisor_id="B12361006",
            jobType="Primary",
            WLS=1,
            POSN_TITLE= "Labor Workers",
            POSN_CODE="S61407",
            startDate=date.today() - timedelta(days=1),  # started in the past
            endDate=date.today() + timedelta(days=10)    # ends in the future
        )

        LaborStatusForm.create(
            studentSupervisee=student2,
            department=inactive_dept,
            termCode_id="202000",
            supervisor_id="B12361006",
            jobType="Primary",
            WLS=1,
            POSN_TITLE= "CS Workers",
            POSN_CODE="S61408",
            startDate=date.today() - timedelta(days=1), 
            endDate=date.today() + timedelta(days=10)   
        )

        LaborStatusForm.create(
            studentSupervisee=student3,
            department=non_active_lab_dep,
            termCode_id="202000",
            supervisor_id="B12361006",
            jobType="Primary",
            WLS=1,
            POSN_TITLE= "Labor Workers",
            POSN_CODE="S61407",
            startDate=date.today() - timedelta(days=1), 
            endDate=date.today() + timedelta(days=10) 
        )
        
        LaborStatusForm.create(
            studentSupervisee=student4,
            department=active_dept,
            termCode_id="202000",
            supervisor_id="B12361006",
            jobType="Primary",
            WLS=1,
            POSN_TITLE= "CS Workers",
            POSN_CODE="S61408",
            startDate=date.today() - timedelta(days=1), 
            endDate=date.today() + timedelta(days=10) 
        )

        LaborStatusForm.create(
            studentSupervisee=student5,
            department=dept,
            termCode_id="202000",
            supervisor_id="B12361006",
            jobType="Primary",
            WLS=1,
            POSN_TITLE= "Labor Workers",
            POSN_CODE="S61407",
            startDate=date.today() + timedelta(days=1), 
            endDate=date.today() - timedelta(days=10)   
        )

        LaborStatusForm.create(
            studentSupervisee=student6,
            department=dept,
            termCode_id="202000",
            supervisor_id="B12361006",
            jobType="Primary",
            WLS=1,
            POSN_TITLE= "Labor Workers",
            POSN_CODE="S61407",
            startDate=date.today() - timedelta(days=1), 
            endDate=date.today() + timedelta(days=10)  
        )
        LaborStatusForm.create(
            studentSupervisee=student7,
            department=case_sensive_name ,
            termCode_id="202000",
            supervisor_id="B12361006",
            jobType="Primary",
            WLS=1,
            POSN_TITLE= "Labor Workers",
            POSN_CODE="S61407",
            startDate=date.today() - timedelta(days=1),  # started in the past
            endDate=date.today() + timedelta(days=10)    # ends in the future
        )
        LaborStatusForm.create(
            studentSupervisee=student8,
            department=case_sensive_name2 ,
            termCode_id="202000",
            supervisor_id="B12361006",
            jobType="Primary",
            WLS=1,
            POSN_TITLE= "Labor Workers",
            POSN_CODE="S61407",
            startDate=date.today() - timedelta(days=1),  # started in the past
            endDate=date.today() + timedelta(days=10)    # ends in the future
        )


        assert stu_user1.laborDepartmentStudent == True
        assert stu_user2.laborDepartmentStudent == False
        assert stu_user3.laborDepartmentStudent == False
        assert stu_user4.laborDepartmentStudent == False
        assert stu_user5.laborDepartmentStudent == False
        assert user_non_stu.laborDepartmentStudent == False
        assert stu_user6.laborDepartmentStudent == True
        assert stu_user7.laborDepartmentStudent == False  #should be false  
        assert stu_user8.laborDepartmentStudent == False
        transaction.rollback()

@pytest.mark.integration
def test_term_model():
    def createLSFandFormHistoryObj(*, termCode):
        """
        Subprocedure to create LSF and FormHistory objects for a particular termCode with dummy data.
        """
        createLSFandFormHistoryObj.callCounter += 1
        Term.get_or_create(termCode=termCode, termName=f"dummyTerm{createLSFandFormHistoryObj.callCounter}")

        #                                        Alex Bryant              Brian Ramsay              CS      
        irrelevantLsfObjData = {'studentSupervisee': 'B00841417', 'supervisor': 'B00763721', 'department': 1, 'jobType': 'Primary', 'WLS': 1, 'POSN_TITLE': '', 'POSN_CODE': ''}
        lsf = LaborStatusForm.create(termCode = termCode, **irrelevantLsfObjData)
        #                                                            Scott Heggen
        irrelevantFhObjData = {'historyType': 'Labor Status Form', 'createdBy': 1, 'createdDate': '2024-01-30', 'status': 'Pending'}
        formHistoryObj = FormHistory.create(formID = lsf, rejectReason = "testing", **irrelevantFhObjData)
        return lsf, formHistoryObj
    createLSFandFormHistoryObj.callCounter = 0
    
    with mainDB.atomic() as transaction:
        # Test that term codes will be ordered by year with ties broken by the last two digits in this order:
        #                                   default
        correctlyOrderedSeasonCodes = ['00', '99', '11', '04', '01', '02', '12', '05', '03', '13']

        # Create the forms out of order
        outOfOrderSeasonCodes = ['13', '02', '04', '00', '11', '12', '03', '99', '01', '05']
        for seasonCode in outOfOrderSeasonCodes:
            createLSFandFormHistoryObj(termCode=int(f'2025{seasonCode}'))

        newForms = FormHistory.select(FormHistory, LaborStatusForm.termCode).join(LaborStatusForm, JOIN.LEFT_OUTER).where(FormHistory.rejectReason == "testing")
        sortedForms = Term.order_by_term(newForms.objects())
        resultingTermCodes = [str(f.termCode) for f in sortedForms]
        resultingSeasonalCodes = [termCode[4:] for termCode in resultingTermCodes]
        assert resultingSeasonalCodes == correctlyOrderedSeasonCodes      

        
        transaction.rollback()

        # Test that the year has more weight in the sort than the seasonal code
        sortedTermCodes = [202311, 202302, 202313, 202400, 202412, 202403]
        unsortedTermCodes = [202302, 202403, 202313, 202311, 202400, 202412]
        for termCodes in unsortedTermCodes:
            createLSFandFormHistoryObj(termCode=int(termCodes))
        newForms = FormHistory.select(FormHistory, LaborStatusForm.termCode).join(LaborStatusForm, JOIN.LEFT_OUTER).where(FormHistory.rejectReason == "testing")
        sortedForms = Term.order_by_term(newForms.objects())
        resultingTermCodes = [f.termCode for f in sortedForms]
        assert  resultingTermCodes == sortedTermCodes
        transaction.rollback()
