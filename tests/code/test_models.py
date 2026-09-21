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
from app.models.formHistory import FormHistory, HistoryType
from app.models.formHistory import Status
from app.models.laborReleaseForm import LaborReleaseForm

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


         # Get or create status records
        try:
            approved_status = Status.get(Status.statusName == "Approved")
        except Status.DoesNotExist:
            approved_status = Status.create(statusName="Approved")
        
        try:
            pending_status = Status.get(Status.statusName == "Pending")
        except Status.DoesNotExist:
            pending_status = Status.create(statusName="Pending")
        
        try:
            denied_status = Status.get(Status.statusName == "Denied")
        except Status.DoesNotExist:
            denied_status = Status.create(statusName="Denied")

        # Get or create history types
        try:
            labor_history_type = HistoryType.get(HistoryType.historyTypeName == "Labor Status Form")
        except HistoryType.DoesNotExist:
            labor_history_type = HistoryType.create(historyTypeName="Labor Status Form")

        try:
            release_history_type = HistoryType.get(HistoryType.historyTypeName == "Labor Release Form")
        except HistoryType.DoesNotExist:
            release_history_type = HistoryType.create(historyTypeName="Labor Release Form")
       
        dept = Department.create(DEPT_NAME="Labor Department", isActive=True, ACCOUNT=6740, ORG=4022) #tests stu_user1 is Labor Student Staff & tests if LSF exists but not within current date
        inactive_dept = Department.create(DEPT_NAME="CS Department", isActive=False, ACCOUNT=6740, ORG=4187) #checks if stu_user2 isn't Labor Dep Student Worker if the dep isn't active 
        non_active_lab_dep = Department.create(DEPT_NAME="Labor Department", isActive=False, ACCOUNT=6740, ORG=4187) #checks if stu_user3 isn't a Labor Dep Student Worker if the Dep isn't active
        active_dept = Department.create(DEPT_NAME="CS Department", isActive=True, ACCOUNT=6740, ORG=4187) #checks if stu_user4 isn't Labor Dep Student Worker if the dep is Active
        case_sensive_name = Department.create(DEPT_NAME="labor department", isActive=True, ACCOUNT=6740, ORG=4187) #checking the case sensitiveness of the department name.
        case_sensive_name2 = Department.create(DEPT_NAME="labour dep", isActive=True, ACCOUNT=6740, ORG=4187) #checking the spelling sensetivity of the department name.

        student1, _ = Student.get_or_create(ID="B12345773")
        student2, _ = Student.get_or_create(ID="B12345783")
        student3, _ = Student.get_or_create(ID="B12345784")
        student4, _ = Student.get_or_create(ID="B12345785")
        student5, _ = Student.get_or_create(ID="B12345786") 
        student6, _ = Student.get_or_create(ID="B12345787") 
        student7, _ = Student.get_or_create(ID="B12345788")
        student8, _ = Student.get_or_create(ID="B12345789")
        student9, _ = Student.get_or_create(ID="B12345790")
        student10, _ = Student.get_or_create(ID="B12345791")
        student11, _ = Student.get_or_create(ID="B12345792")
        student12, _ = Student.get_or_create(ID="B12345793")
   
        # Create users
        stu_user1 = User.create(username="tester",student=student1)
        stu_user2 = User.create(username="inactiveUser", student=student2)
        stu_user3 = User.create(username="inactiveDepartment", student=student3)
        stu_user4 = User.create(username="activeDepartment", student=student4)
        stu_user5 = User.create(username="inActiveTime", student=student5)
        stu_user6 = User.create(username="tester2", student=student6)
        stu_user7 = User.create(username="casesense", student=student7)
        stu_user8 = User.create(username="casesense2", student=student8)
        stu_user9 = User.create(username="unapprovedForm", student=student9)  # Should be FALSE: pending form
        stu_user10 = User.create(username="releasedStudent", student=student10)  # Should be FALSE: has approved release form
        stu_user11 = User.create(username="deniedRelease", student=student11)  # Should be TRUE: has denied release form
        stu_user12 = User.create(username="noForm", student=student12)  # Should be FALSE: no form at all


        # Create Labor Status Forms
        lsf1 = LaborStatusForm.create(
            studentSupervisee=student1,
            department=dept,
            termCode_id="202600",
            supervisor_id="B12361006",
            jobType="Primary",
            WLS=1,
            POSN_TITLE= "Labor Workers",
            POSN_CODE="S61407",
            startDate=date.today() - timedelta(days=1),  # started in the past
            endDate=date.today() + timedelta(days=10)    # ends in the future
        )
        
        lsf2 = LaborStatusForm.create(
            studentSupervisee=student2,
            department=inactive_dept,
            termCode_id="202600",
            supervisor_id="B12361006",
            jobType="Primary",
            WLS=1,
            POSN_TITLE= "CS Workers",
            POSN_CODE="S61408",
            startDate=date.today() - timedelta(days=1), 
            endDate=date.today() + timedelta(days=10)   
        )

        lsf3 = LaborStatusForm.create(
            studentSupervisee=student3,
            department=non_active_lab_dep,
            termCode_id="202600",
            supervisor_id="B12361006",
            jobType="Primary",
            WLS=1,
            POSN_TITLE= "Labor Workers",
            POSN_CODE="S61407",
            startDate=date.today() - timedelta(days=1), 
            endDate=date.today() + timedelta(days=10) 
        )
        
        lsf4 = LaborStatusForm.create(
            studentSupervisee=student4,
            department=active_dept,
            termCode_id="202600",
            supervisor_id="B12361006",
            jobType="Primary",
            WLS=1,
            POSN_TITLE= "CS Workers",
            POSN_CODE="S61408",
            startDate=date.today() - timedelta(days=1), 
            endDate=date.today() + timedelta(days=10) 
        )

        lsf5 = LaborStatusForm.create(
            studentSupervisee=student5,
            department=dept,
            termCode_id="202600",
            supervisor_id="B12361006",
            jobType="Primary",
            WLS=1,
            POSN_TITLE= "Labor Workers",
            POSN_CODE="S61407",
            startDate=date.today() + timedelta(days=1), 
            endDate=date.today() - timedelta(days=10)   
        )

        lsf6 = LaborStatusForm.create(
            studentSupervisee=student6,
            department=dept,
            termCode_id="202600",
            supervisor_id="B12361006",
            jobType="Primary",
            WLS=1,
            POSN_TITLE= "Labor Workers",
            POSN_CODE="S61407",
            startDate=date.today() - timedelta(days=1), 
            endDate=date.today() + timedelta(days=10)  
        )

        lsf7 = LaborStatusForm.create(
            studentSupervisee=student7,
            department=case_sensive_name ,
            termCode_id="202600",
            supervisor_id="B12361006",
            jobType="Primary",
            WLS=1,
            POSN_TITLE= "Labor Workers",
            POSN_CODE="S61407",
            startDate=date.today() - timedelta(days=1),  # started in the past
            endDate=date.today() + timedelta(days=10)    # ends in the future
        )

        lsf8 = LaborStatusForm.create(
            studentSupervisee=student8,
            department=case_sensive_name2 ,
            termCode_id="202600",
            supervisor_id="B12361006",
            jobType="Primary",
            WLS=1,
            POSN_TITLE= "Labor Workers",
            POSN_CODE="S61407",
            startDate=date.today() - timedelta(days=1),  # started in the past
            endDate=date.today() + timedelta(days=10)    # ends in the future
        )

        lsf9 = LaborStatusForm.create(
            studentSupervisee=student9,
            department=dept,
            termCode_id="202600",
            supervisor_id="B12361006",
            jobType="Primary",
            WLS=1,
            POSN_TITLE="Labor Workers",
            POSN_CODE="S61407",
            startDate=date.today() - timedelta(days=1),
            endDate=date.today() + timedelta(days=10)
        )

        lsf10 = LaborStatusForm.create(
            studentSupervisee=student10,
            department=dept,
            termCode_id="202600",
            supervisor_id="B12361006",
            jobType="Primary",
            WLS=1,
            POSN_TITLE="Labor Workers",
            POSN_CODE="S61407",
            startDate=date.today() - timedelta(days=1),
            endDate=date.today() + timedelta(days=10)
        )

        lsf11 = LaborStatusForm.create(
            studentSupervisee=student11,
            department=dept,
            termCode_id="202600",
            supervisor_id="B12361006",
            jobType="Primary",
            WLS=1,
            POSN_TITLE="Labor Workers",
            POSN_CODE="S61407",
            startDate=date.today() - timedelta(days=1),
            endDate=date.today() + timedelta(days=10)
        )

        FormHistory.create(
            formID=lsf1,  
            historyType=labor_history_type,
            createdBy=sup_user,
            createdDate=date.today(),
            reviewedDate=date.today(),
            reviewedBy=sup_user,
            status=approved_status,
            releaseForm=None
        )

        FormHistory.create(
            formID=lsf2,  
            historyType=labor_history_type,
            createdBy=sup_user,
            createdDate=date.today(),
            reviewedDate=date.today(),
            reviewedBy=sup_user,
            status=approved_status,
            releaseForm=None
        )

        FormHistory.create(
            formID=lsf3,  
            historyType=labor_history_type,
            createdBy=sup_user,
            createdDate=date.today(),
            reviewedDate=date.today(),
            reviewedBy=sup_user,
            status=approved_status,
            releaseForm=None
        )

        FormHistory.create(
            formID=lsf4, 
            historyType=labor_history_type,
            createdBy=sup_user,
            createdDate=date.today(),
            reviewedDate=date.today(),
            reviewedBy=sup_user,
            status=approved_status,
            releaseForm=None
        )

        FormHistory.create(
            formID=lsf5,  
            historyType=labor_history_type,
            createdBy=sup_user,
            createdDate=date.today(),
            reviewedDate=date.today(),
            reviewedBy=sup_user,
            status=approved_status,
            releaseForm=None
        )

        FormHistory.create(
            formID=lsf6, 
            historyType=labor_history_type,
            createdBy=sup_user,
            createdDate=date.today(),
            reviewedDate=date.today(),
            reviewedBy=sup_user,
            status=approved_status,
            releaseForm=None
        )

        FormHistory.create(
            formID=lsf7, 
            historyType=labor_history_type,
            createdBy=sup_user,
            createdDate=date.today(),
            reviewedDate=date.today(),
            reviewedBy=sup_user,
            status=approved_status,
            releaseForm=None
        )

        FormHistory.create(
            formID=lsf8,  
            historyType=labor_history_type,
            createdBy=sup_user,
            createdDate=date.today(),
            reviewedDate=date.today(),
            reviewedBy=sup_user,
            status=approved_status,
            releaseForm=None
        )


        # Create pending FormHistory record for student9 (should return False)
        FormHistory.create(
            formID=lsf9,
            historyType=labor_history_type,
            createdBy=sup_user,
            createdDate=date.today(),
            reviewedDate=None,
            reviewedBy=None,
            status=pending_status,
            releaseForm=None
        )

        FormHistory.create(
            formID=lsf10,
            historyType=labor_history_type,
            createdBy=sup_user,
            createdDate=date.today(),
            reviewedDate=date.today(),
            reviewedBy=sup_user,
            status=approved_status,
            releaseForm=None
        )

        FormHistory.create(
            formID=lsf11,
            historyType=labor_history_type,
            createdBy=sup_user,
            createdDate=date.today(),
            reviewedDate=date.today(),
            reviewedBy=sup_user,
            status=approved_status,
            releaseForm=None
        )


        # Create release forms
        release_form10 = LaborReleaseForm.create(
            studentSupervisee=student10,
            department=dept,
            termCode_id="202600",
            supervisor_id="B12361006",
            jobType="Primary",
            WLS=1,
            POSN_TITLE="Labor Workers",
            POSN_CODE="S61407",
            releaseDate=date.today(),
            conditionAtRelease="released",
            reasonForRelease="End of Term",
            contactPerson_id=None
        )

        release_form11 = LaborReleaseForm.create(
            studentSupervisee=student11,
            department=dept,
            termCode_id="202600",
            supervisor_id="B12361006",
            jobType="Primary",
            WLS=1,
            POSN_TITLE="Labor Workers",
            POSN_CODE="S61407",
            releaseDate=date.today(),
            conditionAtRelease="released",
            reasonForRelease="End of Term",
            contactPerson_id=sup_user
        )

        # Create APPROVED release form history for student10 (should exclude them)
        FormHistory.create(
            formID=lsf10,
            historyType=release_history_type,
            createdBy=sup_user,
            createdDate=date.today(),
            reviewedDate=date.today(),
            reviewedBy=sup_user,
            status=approved_status,
            releaseForm=release_form10
        )

        # Create DENIED release form history for student11 (should NOT exclude them)
        FormHistory.create(
            formID=lsf11,
            historyType=release_history_type,
            createdBy=sup_user,
            createdDate=date.today(),
            reviewedDate=date.today(),
            reviewedBy=sup_user,
            status=denied_status,
            releaseForm=release_form11
        )


                # Test assertions
        assert stu_user1.isLaborDepartmentStudent == True
        assert stu_user2.isLaborDepartmentStudent == False
        assert stu_user3.isLaborDepartmentStudent == False
        assert stu_user4.isLaborDepartmentStudent == True  # Active dept with ACCOUNT=6740, ORG=4187
        assert stu_user5.isLaborDepartmentStudent == False
        assert stu_user6.isLaborDepartmentStudent == True
        assert stu_user7.isLaborDepartmentStudent == True  # Valid ORG and ACCOUNT
        assert stu_user8.isLaborDepartmentStudent == True  # Valid ORG and ACCOUNT
        assert stu_user9.isLaborDepartmentStudent == False  # Pending form (not approved)
        assert stu_user10.isLaborDepartmentStudent == False  # Has approved release form
        assert stu_user11.isLaborDepartmentStudent == True  # Has denied release form (still active)
        assert stu_user12.isLaborDepartmentStudent == False  # No form at all
        transaction.rollback()

@pytest.mark.integration
def test_term_model():
    def createLSFandFormHistoryObj(*, termCode):
        """
        Subprocedure to create LSF and FormHistory objects for a particular termCode with dummy data.
        """
        createLSFandFormHistoryObj.callCounter += 1
        Term.get_or_create(termCode=termCode, termName=f"dummyTerm{createLSFandFormHistoryObj.callCounter}")
        assert 1 == 1
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
            createLSFandFormHistoryObj(termCode=int(f'9999{seasonCode}'))   # using an arbitrarily far year to avoid clash

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
