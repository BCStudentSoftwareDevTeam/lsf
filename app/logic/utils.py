from datetime import datetime, date, timedelta, time
from app.models.user import *
from flask import session, request, flash
from urllib.parse import urlparse
from datetime import datetime, timedelta

def makeThirdPartyLink(recipient, host, formHistoryId):
    route = ""
    if recipient == 'SAAS':
        route = "admin/saasOverloadApproval"
    if recipient == 'Financial Aid':
        route = "admin/financialAidOverloadApproval"
    if recipient == 'student':
        route = "studentOverloadApp"

    return f"http://{host}/{route}/{formHistoryId}"

def setReferrerPath():
    session['referrerPath'] = urlparse(request.referrer).path or ''


def adminFlashMessage(user, action, adminType):
    message = "{} has been {} as a {} Admin".format(user.fullName, action, adminType)

    if action == 'added':
        flash(message, "success")
    elif action == 'removed':
        flash(message, "danger") 

# This function calculates the expiration date for a student confirmation and the total date is 30 days from now at 11:59:59 PM
def calculateExpirationDate():
    return datetime.combine(datetime.now() + timedelta(app.config["student_confirmation_days"]),time(23, 59, 59))
