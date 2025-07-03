from peewee import DoesNotExist
from app.models.user import User
from app.logic.tracy import Tracy
from flask import request, flash
from app.logic.userInsertFunctions import createSupervisorFromTracy, createUser
from app.logic.tracy import createStudentFromTracy 


def searchForAdmin(rsp):
    userInput = rsp[1]
    adminType = rsp[0]
    userList = []
    if adminType == "addlaborAdmin":
        tracyStudents = Tracy().getStudentsFromUserInput(userInput)
        students = []
        for student in tracyStudents:
            try:
                existingUser = User.get(User.student == student.ID)
                if existingUser.isLaborAdmin:
                    pass
                else:
                    students.append(student)
            except DoesNotExist as e:
                students.append(student)
        for student in students:
            username = student.STU_EMAIL.split('@', 1)
            userList.append({'username': username[0],
                            'firstName': student.FIRST_NAME,
                            'lastName': student.LAST_NAME,
                            'type': 'Student'
                            })
    tracySupervisors = Tracy().getSupervisorsFromUserInput(userInput)
    supervisors = []
    for supervisor in tracySupervisors:
        try:
            existingUser = User.get(User.supervisor == supervisor.ID)
            if ((existingUser.isLaborAdmin and adminType == "addlaborAdmin")
                or (existingUser.isSaasAdmin and adminType == "addSaasAdmin")
                or (existingUser.isFinancialAidAdmin and adminType == "addFinAidAdmin")):
                pass
            else:
                supervisors.append(supervisor)
        except DoesNotExist as e:
            supervisors.append(supervisor)
    for sup in supervisors:
        username = sup.EMAIL.split('@', 1)
        userList.append({'username': username[0],
                        'firstName': sup.FIRST_NAME,
                        'lastName': sup.LAST_NAME,
                        'type': 'Supervisor'})
    return userList

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


def adminFlashMessage(user, action, adminType):
    message = "{} has been {} as a {} Admin".format(user.fullName, action, adminType)

    if action == 'added':
        flash(message, "success")
    elif action == 'removed':
        flash(message, "danger") 

def addAdmin(newAdmin, adminType):
    if adminType == 'labor':
        newAdmin.isLaborAdmin = True
    if adminType == 'finAid':
        newAdmin.isFinancialAidAdmin = True
    if adminType == 'saas':
        newAdmin.isSaasAdmin = True
    newAdmin.save()

def removeAdmin(oldAdmin, adminType):
    if adminType == 'labor':
        oldAdmin.isLaborAdmin = False
    if adminType == 'finAid':
        oldAdmin.isFinancialAidAdmin = False
    if adminType == 'saas':
        oldAdmin.isSaasAdmin = False
    oldAdmin.save()
