from app.controllers.admin_routes import *
from app.models.user import *
from app.controllers.admin_routes import admin
from app.models.emailTemplate import *
from app.login_manager import require_login
from flask import Flask, redirect, url_for, flash, jsonify, json, request, flash

@admin.route('/admin/emailTemplates', methods=['GET'])
# @login_required
def email_templates():
    currentUser = require_login()
    if not currentUser:                    # Not logged in
        return render_template('errors/403.html'), 403

    if not currentUser.isLaborAdmin:       # Not a labor admin
        if currentUser.student: # logged in as a student
            return redirect('/laborHistory/' + currentUser.student.ID)
        elif currentUser.supervisor:
            return render_template('errors/403.html'), 403

    recipients = EmailTemplate.select(EmailTemplate.audience).distinct()
    return render_template( 'admin/emailTemplates.html', recipients=recipients)

@admin.route('/admin/emailTemplates/getEmailArray/', methods=['GET'])
def getEmailArray():
    templates = EmailTemplate.select()
    return json.dumps([{
                        "ID": template.emailTemplateID,
                        "purpose": template.purpose,
                        "subject": template.subject,
                        "body": template.body,
                        "audience": template.audience,
                        "formType": template.formType,
                        "action": template.action
            } for template in EmailTemplate.select()])

@admin.route('/admin/emailTemplates/getPurpose/<fieldsDictSTR>', methods=['GET'])

def getPurpose(fieldsDictSTR):
    try:
        fieldsDict = json.loads(fieldsDictSTR)
        # populate the Subject field depending on other dropdowns' values
        emailSubjects = EmailTemplate.select(EmailTemplate.subject).where(EmailTemplate.audience == fieldsDict['recipient'], EmailTemplate.formType == fieldsDict['formType'], EmailTemplate.action == fieldsDict['action'])
        subjectList = []
        subjectList.append({"Subject":emailSubjects[0].subject})
        return json.dumps(subjectList)
    except Exception as e:
        print("ERROR in getPurpose(): ", e)
        return jsonify({"Success": False}), 500

@admin.route('/admin/emailTemplates/getEmail/<fieldsDictSTR>', methods=['GET'])

def getEmail(fieldsDictSTR):
    try:
        fieldsDict = json.loads(fieldsDictSTR)
        email = EmailTemplate.get(EmailTemplate.action == fieldsDict["action"], EmailTemplate.audience == fieldsDict["recipient"], EmailTemplate.formType == fieldsDict["formType"])
        purposeList = {"emailBody": email.body, "emailSubject": email.subject}
        return json.dumps(purposeList)
    except Exception as e:
        print("ERROR getEmail(): ", e)
        return jsonify({"Success": False})

@admin.route('/admin/emailTemplates/postEmail', methods=['POST'])
def postEmail():
    try:
        email = EmailTemplate.get(EmailTemplate.audience == request.form['recipient'], EmailTemplate.formType == request.form['formType'], EmailTemplate.action == request.form['action'])
        email.body = request.form['body']
        email.subject = request.form["purpose"]
        email.save()
        message = "The Email Template '{0} {1} {2}' has been successfully updated.".format(email.audience, email.formType, email.action)
        flash(message, "success")
        return (jsonify({"Success": True}))
    except Exception as e:
        print("ERROR in postEmail: ", e)
        return jsonify({"Success": False})
