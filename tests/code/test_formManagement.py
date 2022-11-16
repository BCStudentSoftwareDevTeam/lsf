import pytest
from app.logic.formManagement import *

@pytest.mark.integration
def test_createLaborStatusForm():
    student = "B00730361"
    supervisor = "B12361006"
    dept = ""
    term = ""
    formData = {
        "stuStartDate":""
    }
    new_lsf = createLaborStatusForm(student, supervisor, dept, term, formData)

    # Test success conditions
    supervisor = createSupervisorFromTracy(username="heggens", bnumber="B12361006")
    assert supervisor.FIRST_NAME == "Scott"

    supervisor = createSupervisorFromTracy(username="", bnumber="B12361006")
    assert supervisor.FIRST_NAME == "Scott"

    supervisor = createSupervisorFromTracy(bnumber="B12361006")
    assert supervisor.FIRST_NAME == "Scott"

    supervisor = createSupervisorFromTracy(username="heggens")
    assert supervisor.FIRST_NAME == "Scott"

    supervisor = createSupervisorFromTracy(username="heggens", bnumber="")
    assert supervisor.FIRST_NAME == "Scott"

    supervisor = createSupervisorFromTracy("heggens")
    assert supervisor.FIRST_NAME == "Scott"

    # Tests getting a supervisor from TRACY that does not exist in the supervisor table
    supervisor = createSupervisorFromTracy(username="hoffmanm", bnumber="B1236237")
    assert supervisor.FIRST_NAME == "Megan"
    supervisor.delete_instance()

    supervisor = createSupervisorFromTracy(username="", bnumber="B1236237")
    assert supervisor.FIRST_NAME == "Megan"
    supervisor.delete_instance()

    supervisor = createSupervisorFromTracy(username="hoffmanm")
    assert supervisor.FIRST_NAME == "Megan"
    supervisor.delete_instance()
