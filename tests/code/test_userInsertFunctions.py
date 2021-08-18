import pytest
from app.logic.userInsertFunctions import *

@pytest.mark.integration
def test_createSupervisorFromTracy():
    # Test fail conditions
    with pytest.raises(ValueError):
        supervisor = createSupervisorFromTracy()

    with pytest.raises(InvalidUserException):
        supervisor = createSupervisorFromTracy("B12361006")

    with pytest.raises(InvalidUserException):
        supervisor = createSupervisorFromTracy(username="B12361006")

    with pytest.raises(InvalidUserException):
        supervisor = createSupervisorFromTracy(bnumber="heggens")

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

@pytest.mark.integration
def test_createStudentFromTracy():
    # Test fail conditions
    with pytest.raises(ValueError):
        student = createStudentFromTracy()

    with pytest.raises(InvalidUserException):
        student = createStudentFromTracy("B00730361")

    with pytest.raises(InvalidUserException):
        student = createStudentFromTracy(username="B00730361")

    with pytest.raises(InvalidUserException):
        student = createStudentFromTracy(bnumber="jamalie")

    # Test success conditions
    student = createStudentFromTracy(username="jamalie", bnumber="B00730361")
    assert student.FIRST_NAME == "Elaheh"

    student = createStudentFromTracy(username="", bnumber="B00730361")
    assert student.FIRST_NAME == "Elaheh"

    student = createStudentFromTracy(bnumber="B00730361")
    assert student.FIRST_NAME == "Elaheh"

    student = createStudentFromTracy(username="jamalie")
    assert student.FIRST_NAME == "Elaheh"

    student = createStudentFromTracy(username="jamalie", bnumber="")
    assert student.FIRST_NAME == "Elaheh"

    student = createStudentFromTracy("jamalie")
    assert student.FIRST_NAME == "Elaheh"

    # Tests getting a student from TRACY that does not exist in the student table
    student = createStudentFromTracy(username="adamskg", bnumber="B00785329")
    assert student.FIRST_NAME == "Kat"
    student.delete_instance()

    student = createStudentFromTracy(username="", bnumber="B00785329")
    assert student.FIRST_NAME == "Kat"
    student.delete_instance()

    student = createStudentFromTracy(username="adamskg")
    assert student.FIRST_NAME == "Kat"
    student.delete_instance()

@pytest.mark.integration
def test_getOrCreateStudentRecord():
    # Test fail conditions
    with pytest.raises(ValueError):
        student = getOrCreateStudentRecord()

    with pytest.raises(InvalidUserException):
        student = getOrCreateStudentRecord("B00730361")

    with pytest.raises(InvalidUserException):
        student = getOrCreateStudentRecord(username="B00730361")

    with pytest.raises(InvalidUserException):
        student = getOrCreateStudentRecord(bnumber="jamalie")

    # Test success conditions
    student = getOrCreateStudentRecord(username="jamalie", bnumber="B00730361")
    assert student.FIRST_NAME == "Elaheh"

    student = getOrCreateStudentRecord(username="", bnumber="B00730361")
    assert student.FIRST_NAME == "Elaheh"

    student = getOrCreateStudentRecord(bnumber="B00730361")
    assert student.FIRST_NAME == "Elaheh"

    student = getOrCreateStudentRecord(username="jamalie")
    assert student.FIRST_NAME == "Elaheh"

    student = getOrCreateStudentRecord(username="jamalie", bnumber="")
    assert student.FIRST_NAME == "Elaheh"

    student = getOrCreateStudentRecord("jamalie")
    assert student.FIRST_NAME == "Elaheh"

    # Test getting a student that does not exist in Tracy
    student = getOrCreateStudentRecord(bnumber="B00841417")
    assert student.FIRST_NAME == "Alex"

    student = getOrCreateStudentRecord(username="bryantal")
    assert student.FIRST_NAME == "Alex"


    # Tests getting a student from TRACY that does not exist in the student table
    student = getOrCreateStudentRecord(username="adamskg", bnumber="B00785329")
    assert student.FIRST_NAME == "Kat"
    student.delete_instance()

    student = getOrCreateStudentRecord(username="", bnumber="B00785329")
    assert student.FIRST_NAME == "Kat"
    student.delete_instance()

    student = getOrCreateStudentRecord(username="adamskg")
    assert student.FIRST_NAME == "Kat"
    student.delete_instance()


