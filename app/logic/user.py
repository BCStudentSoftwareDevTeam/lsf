from flask import request
from peewee import DoesNotExist
from app.models.user import User
from app.logic.tracy import Tracy
from app.logic.userInsertFunctions import createUser, createSupervisorFromTracy, createStudentFromTracy
from app.models.supervisor import Supervisor
from app.models.student import Student
from flask import flash

def getUser(selectpickerID):
    username = request.form.get(selectpickerID)
    try:
        user = User.get(User.username == username)
    except DoesNotExist as e:
        usertype = Tracy().checkStudentOrSupervisor(username)
        supervisor = student = None
        if usertype == "Student":
            student = createStudentFromTracy(username)
        else:
            supervisor = createSupervisorFromTracy(username)
        user = createUser(username, student=student, supervisor=supervisor)
    return user


def flashMessage(user, action, adminType):
    message = "{} has been {} as a {} Admin".format(user.fullName, action, adminType)

    if action == 'added':
        flash(message, "success")
    elif action == 'removed':
        flash(message, "danger") 