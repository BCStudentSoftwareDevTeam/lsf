from peewee import DoesNotExist
from app.models.user import User
from flask import request, flash
from app.logic.userInsertFunctions import createStudentFromTracy, createSupervisorFromTracy, createUser
from app.models.supervisor import Supervisor
from app.models.student import Student
from app.logic.tracy import Tracy

def searchForAdmin(rsp):
    userInput = rsp[1]
    adminType = rsp[0]
    userList = []
    if adminType == "addlaborAdmin":
        databaseStudents = Student.select().where(Student.legal_name.contains(userInput) | Student.preferred_name.contains(userInput)| Student.LAST_NAME.contains(userInput)) 
        students = []
        for student in databaseStudents:
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
    databaseSupervisors = Supervisor.select().where(Supervisor.legal_name.contains(userInput) | Supervisor.preferred_name.contains(userInput)| Supervisor.LAST_NAME.contains(userInput))
    supervisors = []
    for supervisor in databaseSupervisors:
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
