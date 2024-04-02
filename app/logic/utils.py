from flask import session, request
from urllib.parse import urlparse


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
