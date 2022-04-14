from app.controllers.admin_routes import *
from app.models.user import User
from app.controllers.admin_routes import admin
from app.login_manager import require_login
from app.models.term import Term
from datetime import datetime
from flask import json, jsonify
from flask import request, redirect
from peewee import IntegrityError

@admin.route('/admin/termManagement', methods=['GET', 'POST'])
# @login_required

def term_Management():
    currentUser = require_login()
    if not currentUser:                    # Not logged in
        return render_template('errors/403.html')
    if not currentUser.isLaborAdmin:       # Not an admin
        if currentUser.student: # logged in as a student
            return redirect('/laborHistory/' + currentUser.student.ID)
        elif currentUser.supervisor:
            return render_template('errors/403.html'), 403

    today = datetime.now()
    termsByYear ={}
    for termYear in range(today.year-2, today.year+3):
        createTerms(termYear)
        termsByYear[termYear] = list(Term.select().where(Term.termCode.cast('char').contains(termYear)))

    return render_template( 'admin/termManagement.html',
                             title='Term Management',
                             listOfTerms = termsByYear
                          )

def createTerms(termYear):
    """
        This function creates the terms for the given Academic Year
    """
    code = termYear * 100
    for i in range(8):
        try:
            if i == 0:
                Term.create(termCode = code, termName = "AY {}-{}".format(termYear, termYear + 1), isAcademicYear=True)
            elif i == 1:
                Term.create(termCode = (code + 11), termName = "Fall {}".format(termYear))
            elif i == 7:
                Term.create(termCode = (code + 4), termName = "Fall Break {}".format(termYear), isBreak=True)
            elif i == 2:
                Term.create(termCode = (code + 1), termName = "Thanksgiving Break {}".format(termYear), isBreak=True)
            elif i == 3:
                Term.create(termCode = (code + 2), termName = "Christmas Break {}".format( termYear), isBreak=True)
            elif i == 4:
                Term.create(termCode = (code + 12), termName = "Spring {}".format(termYear + 1))
            elif i == 5:
                Term.create(termCode = (code + 3), termName = "Spring Break {}".format(termYear + 1), isBreak=True)
            elif i == 6:
                Term.create(termCode = (code + 13), termName = "Summer {}".format(termYear + 1), isBreak=True, isSummer=True)
        except IntegrityError as e:
            pass

@admin.route("/termManagement/setDate/", methods=['POST'])
def ourDate():
    """ This function updates the dates so that they are correctly formatted to be inserted into the
    database.
    """
    try:
        rsp = eval(request.data.decode("utf-8"))
        if rsp:
            termCode = rsp['termCode']
            termToChange = Term.get(Term.termCode == termCode)
            date_value = rsp.get("start", rsp.get("end", rsp.get("primaryCutOff", rsp.get("adjustmentCutOff", None))))
            if rsp.get('start', None):
                startDate = datetime.strptime(date_value, '%m/%d/%Y').strftime('%Y-%m-%d')
                termToChange.termStart = startDate
                dateChanged = 'Start Date'
            if rsp.get('end', None):
                endDate = datetime.strptime(date_value, '%m/%d/%Y').strftime('%Y-%m-%d')
                termToChange.termEnd = endDate
                dateChanged = 'End Date'
            if rsp.get('primaryCutOff', None):
                primaryCutOff = datetime.strptime(date_value, '%m/%d/%Y').strftime('%Y-%m-%d')
                termToChange.primaryCutOff = primaryCutOff
                dateChanged = 'Primary Cut Off Date'
            if rsp.get('adjustmentCutOff', None):
                adjustmentCutOff = datetime.strptime(date_value, '%m/%d/%Y').strftime('%Y-%m-%d')
                termToChange.adjustmentCutOff = adjustmentCutOff
                dateChanged = 'Adjustment Cut Off Date'
            termToChange.save()
            flasherInfo = {'changedTerm': termToChange.termName,
                            'newDate': date_value,
                            'dateChanged': dateChanged
            }
            return jsonify(flasherInfo)
    except Exception as e:
        print("You have failed to update the date.", e)
        return jsonify({"Success": False})


@admin.route('/termManagement/manageStatus', methods=['POST'])
def termStatusCheck():
    """ This function updates the state of the term
    """
    try:
        rsp = eval(request.data.decode("utf-8")) # This fixes byte indices must be intergers or slices error
        if rsp:
            term = Term.get(rsp['termBtn'])

            if term.termState == True:
                term.termState = False
            elif term.termState == False:
                term.termState = True
            term.save()
            flasherInfo = {'termChanged': term.termName}
            return jsonify(flasherInfo)
    except Exception as e:
        print(e)
        return jsonify({"Success": False})

@admin.route('/termManagement/manageEval', methods=['POST'])
def manageEval():
    try:
        rsp = eval(request.data.decode("utf-8")) # This fixes byte indices must be integers or slices error
        if rsp:
            term = Term.get(rsp['evalBtn'])
            if rsp["isMidyear"]:
                term.isMidyearEvaluationOpen = not term.isMidyearEvaluationOpen
                term.isFinalEvaluationOpen = False
            else:
                term.isFinalEvaluationOpen = not term.isFinalEvaluationOpen
                term.isMidyearEvaluationOpen = False
            term.save()
            flasherInfo = {'termChanged': term.termName}
            return jsonify(flasherInfo)
    except Exception as e:
        print(e)
        return jsonify({}, 500)
