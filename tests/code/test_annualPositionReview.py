import pytest
from app import app
from app.models import mainDB
from app.models.term import Term
from app.models.department import Department
from app.models.supervisor import Supervisor
from app.models.supervisorDepartment import SupervisorDepartment
from app.models.emailTemplate import EmailTemplate
from app.models.user import User
from app.models.positionHistory import PositionHistory


from app.logic.emailHandler import emailHandler




@pytest.mark.integration
def test_sendAnnualPositionReviewRequests():
    with app.app_context():
        with mainDB.atomic() as transaction:
            Department.update(isActive=False).where(Department.isActive == True).execute()


            term, wasCreated = Term.get_or_create(
                termCode=209900,
                defaults={"termName": "AY 2099-2100", "isAcademicYear": True}
            )


            department, wasCreated = Department.get_or_create(
                DEPT_NAME="Test Department", ACCOUNT="1234", ORG="9999",
                defaults={"isActive": True}
            )
            emptyDepartment, wasCreated = Department.get_or_create(
                DEPT_NAME="Empty Department", ACCOUNT="4321", ORG="9998",
                defaults={"isActive": True}
            )

            # "Test Department" has one active position that should get marked
            # reviewed, and one inactive position that should be left alone.
            activePosition = PositionHistory.create(
                positionTitle="Lab Assistant", positionCode="TESTPOS1", department=department,
                status="Active", revisionDate="2020-01-01"
            )
            inactivePosition = PositionHistory.create(
                positionTitle="Retired Role", positionCode="TESTPOS2", department=department,
                status="Inactive", revisionDate="2020-01-01"
            )

            # "Empty Department" has no supervisors/coordinators, but does have an
            # active position - it should still get marked reviewed even though no
            # email goes out for it.
            emptyDeptPosition = PositionHistory.create(
                positionTitle="Office Assistant", positionCode="TESTPOS3", department=emptyDepartment,
                status="Active", revisionDate="2020-01-01"
            )


            coordinator, wasCreated = Supervisor.get_or_create(
                ID="B00000001",
                defaults={"LAST_NAME": "Coordinator", "EMAIL": "coordinator@example.com", "legal_name": "Cory Coordinator"}
            )
            supervisor, wasCreated = Supervisor.get_or_create(
                ID="B00000002",
                defaults={"LAST_NAME": "Supervisor", "EMAIL": "supervisor@example.com", "legal_name": "Sam Supervisor"}
            )
            SupervisorDepartment.get_or_create(supervisor=coordinator, department=department, defaults={"isCoordinator": True})
            SupervisorDepartment.get_or_create(supervisor=supervisor, department=department, defaults={"isCoordinator": False})


            EmailTemplate.get_or_create(
                purpose="Annual Position Review Request",
                defaults={
                    "formType": "Position Review",
                    "action": "Annual Request",
                    "subject": "Annual Position Review - @@AcademicYear@@",
                    "body": "<p>@@Department@@ - @@AcademicYear@@</p>",
                    "audience": "Department",
                }
            )


            admin, wasCreated = User.get_or_create(username="test_position_review_admin", defaults={"isLaborAdmin": True})


            ################ SENDING REQUESTS ################
            handler = emailHandler(termCodeUnderReview=term.termCode)
            result = handler.sendAnnualPositionReviewRequests(admin)


            # Only "Test Department" has supervisors/coordinators, so only it gets an email.
            assert result["sentCount"] == 1
            assert result["departmentCount"] == 2


            activePosition = PositionHistory.get(PositionHistory.positionCode == "TESTPOS1")
            assert activePosition.academicYear == term
            assert activePosition.requestedBy.userID == admin.userID
            firstRequestedOn = activePosition.requestedOn

            # The inactive position is left untouched - reviewing only stamps active ones.
            inactivePosition = PositionHistory.get(PositionHistory.positionCode == "TESTPOS2")
            assert inactivePosition.requestedBy is None


            # The active position in "Empty Department" is still marked (the request
            # was made), it just doesn't count toward sentCount since no email went out.
            emptyDeptPosition = PositionHistory.get(PositionHistory.positionCode == "TESTPOS3")
            assert emptyDeptPosition.requestedBy.userID == admin.userID


            ################ RE-SENDING SHOULD UPDATE, NOT DUPLICATE ################
            handler.sendAnnualPositionReviewRequests(admin)


            positions = PositionHistory.select().where(
                PositionHistory.department == department,
                PositionHistory.status == "Active"
            )
            assert positions.count() == 1
            assert positions.get().requestedOn >= firstRequestedOn


            transaction.rollback()


