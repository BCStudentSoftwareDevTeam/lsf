from app.controllers.main_routes import *
from app.login_manager import require_login
from app.logic.tracy import Tracy, InvalidQueryException
from app.models.student import Student
from app.models.laborStatusForm import LaborStatusForm
from app.models.department import Department
from app.models.formHistory import FormHistory
from flask import jsonify, render_template
import re

def usernameFromEmail(email):
    # split always returns a list, even if there is nothing to split, so [0] is safe
    return email.split('@',1)[0]

# Convert a Student or STUDATA record into the dictionary that our js expects
def studentDbToDict(item):
    return {'username': usernameFromEmail(item.STU_EMAIL.strip()),
            'firstName': item.FIRST_NAME.strip(),
            'lastName': item.LAST_NAME.strip(),
            'bnumber': item.ID.strip(),
            'type': 'Student'}

@main_bp.route('/main/search',  methods=['GET'])
def search_page():
    currentUser = require_login()
    if not currentUser or not currentUser.supervisor:
        return render_template('errors/403.html'), 403

    return render_template( 'main/search.html' )

# search student table and STUDATA for student results
@main_bp.route('/main/search/<query>',  methods=['GET'])
def search(query=None):
    currentUser = require_login()
    if not currentUser or not currentUser.supervisor:
        return render_template('errors/403.html'), 403

    current_students = []
    our_students = []
    query = query.strip()

    # bnumber search
    # '[Bb]\d+' == is the search a bnumber
    if re.match('[Bb]\d+', query):
        our_students = list(map(studentDbToDict, Student.select().where(Student.ID % "{}%".format(query.upper()))))
        current_students = list(map(studentDbToDict, Tracy().getStudentsFromBNumberSearch(query)))

    # name search
    else:
        if " " not in query:
            search = query.upper() + "%"
            results = Student.select().where(Student.FIRST_NAME ** search | Student.LAST_NAME ** search)
        else:
            search = query.split()
            first_query = search[0] + "%"
            last_query = search[1] + "%"
            results = Student.select().where(Student.FIRST_NAME ** first_query & Student.LAST_NAME ** last_query)

        our_students = list(map(studentDbToDict, results))
        current_students = list(map(studentDbToDict, Tracy().getStudentsFromUserInput(query)))

    # combine lists, remove duplicates, and then sort
    students = list({v['bnumber']:v for v in (current_students + our_students)}.values())
    students = sorted(students, key=lambda f:f['firstName'] + f['lastName'])
    if currentUser.isLaborAdmin or currentUser.isFinancialAidAdmin or currentUser.isSaasAdmin:
        return jsonify(students)
    else:
        newstudents = []
        departments = list(FormHistory.select(FormHistory.formID.department.DEPT_NAME)
                        .join_from(FormHistory, LaborStatusForm)
                        .join_from(LaborStatusForm, Department)
                        .where((FormHistory.formID.supervisor == currentUser.supervisor.ID) | (FormHistory.createdBy == currentUser))
                        .order_by(FormHistory.formID.department.DEPT_NAME.asc())
                        .distinct()
                        )
        for student in students:
            student_in_department = (FormHistory.select(FormHistory.formID.department.DEPT_NAME)
                        .join_from(FormHistory, LaborStatusForm)
                        .join_from(LaborStatusForm, Department)
                        .where((FormHistory.formID.studentSupervisee == student['bnumber']) & FormHistory.formID.department.DEPT_NAME in departments)
                        .order_by(FormHistory.formID.department.DEPT_NAME.asc())
                        .distinct()
                        )
            if student_in_department:
                newstudents.append(student)
        return jsonify(newstudents)
