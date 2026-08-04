import pytest
from app import app
from app.models import mainDB
from app.models.term import Term
from app.models.department import Department
from app.models.supervisor import Supervisor
from app.models.supervisorDepartment import SupervisorDepartment
from app.models.emailTemplate import EmailTemplate
from app.models.user import User
from app.models.positionReview import PositionReview


from app.logic.annualPositionReview import sendAnnualPositionReviewRequests




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
            result = sendAnnualPositionReviewRequests(term.termCode, admin)


            # Only "Test Department" has supervisors/coordinators, so only it gets an email.
            assert result["sentCount"] == 1
            assert result["departmentCount"] == 2


            review = PositionReview.get(
                PositionReview.academicYear == term,
                PositionReview.department == department
            )
            assert review.requestedBy.userID == admin.userID
            firstRequestedOn = review.requestedOn


            # A record is still made for Empty Department (the request was made),
            # it just doesn't count toward sentCount since no email went out.
            emptyReview = PositionReview.get(
                PositionReview.academicYear == term,
                PositionReview.department == emptyDepartment
            )
            assert emptyReview.requestedBy.userID == admin.userID


            ################ RE-SENDING SHOULD UPDATE, NOT DUPLICATE ################
            sendAnnualPositionReviewRequests(term.termCode, admin)


            reviews = PositionReview.select().where(
                PositionReview.academicYear == term,
                PositionReview.department == department
            )
            assert reviews.count() == 1
            assert reviews.get().requestedOn >= firstRequestedOn


            transaction.rollback()


