import pytest
from app.models.Tracy.studata import STUDATA
from app.models.Tracy.stustaff import STUSTAFF
from app.models import mainDB
from app.models.student import Student
from app.models.supervisor import Supervisor
from app.models.department import Department
from app.models.Tracy import db
from app.models.Tracy.studata import STUDATA
from app.logic.tracy import Tracy
from app.logic.userInsertFunctions import *

@pytest.mark.integration
def test_createSupervisorFromTracy():
    # Test fail conditions
    with pytest.raises(InvalidUserException):
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

@pytest.mark.integration
def test_updateSupervisorFromTracy():
    user = User.get(username="heggens")
    assert user.fullName == "Scott Heggen"

    tracyEntry = Tracy().getSupervisorFromID(user.supervisor_id)
    tracyEntry.FIRST_NAME="NotScott"
    tracyEntry.LAST_NAME="NotHeggen"
    db.session.commit()

    user = updateUserFromTracy(user)
    assert user.fullName == "NotScott NotHeggen"

    dbuser = User.get(username="heggens")
    assert dbuser.fullName == "NotScott NotHeggen", "The object changed but not the database"

    tracyEntry.FIRST_NAME="Scott"
    tracyEntry.LAST_NAME="Heggen"
    db.session.commit()

    dbuser.supervisor.legal_name="Scott"
    dbuser.supervisor.LAST_NAME="Heggen"
    dbuser.supervisor.save()

@pytest.mark.integration
def test_updateStudentFromTracy():
    user = User.get(username="jamalie")
    assert user.fullName == "Elaheh Jamali"

    tracyEntry = Tracy().getStudentFromBNumber(user.student_id)
    tracyEntry.FIRST_NAME="NotElaheh"
    tracyEntry.LAST_NAME="NotJamali"
    db.session.commit()

    user = updateUserFromTracy(user)
    assert user.fullName == "NotElaheh NotJamali"

    dbuser = User.get(username="jamalie")
    assert dbuser.fullName == "NotElaheh NotJamali", "The object changed but not the database"

    tracyEntry.FIRST_NAME="Elaheh"
    tracyEntry.LAST_NAME="Jamali"
    db.session.commit()

    dbuser.student.legal_name="Elaheh"
    dbuser.student.LAST_NAME="Jamali"
    dbuser.student.save()

@pytest.mark.integration
def test_updateDBRecords():
    with mainDB.atomic() as transaction:
        incorrectStudent = Student.create(ID="B00751360", PIDM=2345, legal_name="NotTyler", LAST_NAME="Parton")
        updateRecordIncorrectly = Supervisor.update(legal_name="NotMadina").where(Supervisor.ID == "B00769499").execute()
        incorrectSupervisor = Supervisor.get(Supervisor.ID == "B00769499")
        updateStudentRecord(incorrectStudent)
        updateSupervisorRecord(incorrectSupervisor)

        assert incorrectStudent.FIRST_NAME == "Tyler"
        assert incorrectSupervisor.FIRST_NAME == "Madina"

        incorrectDepartment = Department.create(DEPT_NAME="English", ACCOUNT="0000", ORG="0000", departmentCompliance = 1)
        updateDepartment(incorrectDepartment)

        assert "0000" != incorrectDepartment.ACCOUNT
        assert "0000" != incorrectDepartment.ORG

        transaction.rollback()
