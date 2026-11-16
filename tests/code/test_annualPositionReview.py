import pytest
from datetime import date
from app import app
from app.models import mainDB
from app.models.term import Term
from app.models.department import Department
from app.models.supervisor import Supervisor
from app.models.supervisorDepartment import SupervisorDepartment
from app.models.emailTemplate import EmailTemplate
from app.models.positionHistory import PositionHistory
from app.logic.emailHandler import emailHandler
from app.logic.getPositions import getPositionReviewCutoff


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

            # "Test Department" has one active position that should get flagged, and one inactive position that should be left alone.
            activePosition = PositionHistory.create(
                positionTitle="Lab Assistant", positionCode="TESTPOS1", department=department,
                status="Active", revisionDate="2020-01-01"
            )
            inactivePosition = PositionHistory.create(
                positionTitle="Retired Role", positionCode="TESTPOS2", department=department,
                status="Inactive", revisionDate="2020-01-01"
            )

            # "Empty Department" has no supervisors/coordinators, so no email goes out for it.
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


            # Revised recently, so it isn't due for review yet.
            recentPosition = PositionHistory.create(
                positionTitle="Recently Revised Role", positionCode="TESTPOS5", department=department,
                status="Active", revisionDate=date.today()
            )


            ################ SENDING REQUESTS ################
            handler = emailHandler(termCodeUnderReview=term.termCode)
            result = handler.sendAnnualPositionReviewRequests()


            # Only "Test Department" has supervisors/coordinators, so only it gets an email.
            assert result["sentCount"] == 1
            assert result["departmentCount"] == 2
            assert result["failedDepartments"] == []
            assert result["noReviewDueDepartments"] == []

            # Revised over 5 years ago, so it's due and gets flagged.
            activePosition = PositionHistory.get(PositionHistory.positionCode == "TESTPOS1")
            assert activePosition.reviewRequested is True

            # The inactive position is left untouched - only active ones are flagged.
            inactivePosition = PositionHistory.get(PositionHistory.positionCode == "TESTPOS2")
            assert inactivePosition.reviewRequested is False

            # Revised within the last 5 years, so it isn't part of the request.
            recentPosition = PositionHistory.get(PositionHistory.positionCode == "TESTPOS5")
            assert recentPosition.reviewRequested is False

            # No email went out for "Empty Department" (nobody to send to), so its
            # position stays unflagged and it can still be requested once someone is assigned.
            emptyDeptPosition = PositionHistory.get(PositionHistory.positionCode == "TESTPOS3")
            assert emptyDeptPosition.reviewRequested is False


            ################ RE-SENDING SHOULD NOT EMAIL AGAIN ################
            result = handler.sendAnnualPositionReviewRequests()

            assert result["sentCount"] == 0
            assert result["noReviewDueDepartments"] == ["Test Department"]


            ################ ANOTHER OUTDATED POSITION MAKES THE DEPARTMENT DUE AGAIN ################
            PositionHistory.create(
                positionTitle="Old Role", positionCode="TESTPOS4", department=department,
                status="Active", revisionDate="2020-01-01"
            )
            result = handler.sendAnnualPositionReviewRequests()

            assert result["sentCount"] == 1
            assert PositionHistory.get(PositionHistory.positionCode == "TESTPOS4").reviewRequested is True


            transaction.rollback()


@pytest.mark.unit
def test_getPositionReviewCutoff():
    assert getPositionReviewCutoff(date(2026, 11, 16)) == date(2021, 11, 16)
    # Feb 29 has no counterpart 5 years earlier, so it falls back to Feb 28.
    assert getPositionReviewCutoff(date(2028, 2, 29)) == date(2023, 2, 28)
