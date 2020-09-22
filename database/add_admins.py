# Add admins for testing
from app.logic.userInsertFunctions import *

students = ['manalaih','mupotsal','escalerapadronl','cruzg','romanow','crafta','rieral','juem','jamalie']
staff = ['bryantal','ramsayb2','heggens','knowlesg', 'welshs', 'napoleonr2', 'buenrostroa', 'ashb', 'gosneyj', 'asantes']

print("Adding staff admins")
for s in staff:
    obj = createSupervisorFromTracy(s)
    createUser(s, supervisor=obj)
    u = User.get(username=s)
    u.isLaborAdmin = True
    u.save()

print("Adding student admins")
for s in students:
    obj = createStudentFromTracy(s)
    createUser(s, student=obj)
    u = User.get(username=s)
    u.isLaborAdmin = True
    u.save()
