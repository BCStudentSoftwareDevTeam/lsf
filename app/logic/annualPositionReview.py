from datetime import datetime

from flask_mail import Mail, Message

from app import app
from app.models.department import Department
from app.models.emailTemplate import EmailTemplate
from app.models.positionReview import PositionReview
from app.models.term import Term
from app.logic.getSupervisors import getSupervisors


def sendMail(mail, message: Message):
    if app.config['ENV'] == 'production' or app.config['ALWAYS_SEND_MAIL']:

        # If we have set an override address
        if app.config['MAIL_OVERRIDE_ALL']:
            message.html = "<b>Original message intended for {}.</b><br>".format(", ".join(message.recipients)) + message.html
            message.recipients = [app.config['MAIL_OVERRIDE_ALL']]

        message.reply_to = app.config["REPLY_TO_ADDRESS"]
        mail.send(message)

    elif app.config['ENV'] == 'testing':
        pass
    else:
        print("ENV: {}. Email not sent to {}, subject '{}'.".format(app.config['ENV'], message.recipients, message.subject))


def sendAnnualPositionReviewRequests(academicYearTermCode, requestingUser):
    """
    Sends an Annual Position Review request email to every active department's
    Labor Coordinators and supervisors, and records that the request was made
    for the given academic year.
    """
    mail = Mail(app)
    term = Term.get(Term.termCode == academicYearTermCode)
    template = EmailTemplate.get(EmailTemplate.purpose == "Annual Position Review Request")
    departments = Department.select().where(Department.isActive == True)

    sentCount = 0
    for department in departments:
        # A review is considered "requested" for every active department as soon
        # as this runs, whether or not there's currently anyone to email - a
        # department with no supervisors/coordinators assigned is itself worth
        # surfacing, not skipping the department.
        existingReview = PositionReview.get_or_none(
            PositionReview.academicYear == term,
            PositionReview.department == department
        )
        if existingReview:
            existingReview.requestedOn = datetime.now()
            existingReview.requestedBy = requestingUser
            existingReview.save()
        else:
            PositionReview.create(
                academicYear=term,
                department=department,
                requestedOn=datetime.now(),
                requestedBy=requestingUser
            )

        supervisors, laborCoordinators = getSupervisors(department)
        recipients = {person["email"] for person in supervisors + laborCoordinators if person["email"]}
        if not recipients:
            continue

        subject = template.subject.replace("@@AcademicYear@@", term.termName)
        body = template.body.replace("@@Department@@", department.DEPT_NAME).replace("@@AcademicYear@@", term.termName)

        message = Message(subject, recipients=list(recipients))
        message.html = body
        sendMail(mail, message)

        sentCount += 1

    return {"sentCount": sentCount, "departmentCount": departments.count()}

