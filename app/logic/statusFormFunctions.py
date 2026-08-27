from app.models.overloadForm import *
from datetime import datetime, date, timedelta, time
from app.models.laborStatusForm import *
from app.logic.userInsertFunctions import InvalidUserException
from app.models.formHistory import*
from app.logic.emailHandler import emailHandler
from app.logic.utils import makeThirdPartyLink, calculateExpirationDate
from app.logic.tracy import Tracy, InvalidQueryException
from flask import request, json, jsonify
from functools import reduce
import operator


def createLaborStatusForm(student, primarySupervisor, department, term, rspFunctional):
    """
    Creates a labor status form with the appropriate data passed from userInsert() in laborStatusForm.py
    studentID: student's primary ID in the database AKA their B#
    primarySupervisor: primary supervisor of the student
    department: department the position is a part of
    term: term when the position will happen
    rspFunctional: a dictionary containing all the data submitted in the LSF page
    returns the laborStatusForm object just created for later use in laborStatusForm.py
    """
    # Changes the dates into the appropriate format for the table
    startDate = datetime.strptime(rspFunctional['stuStartDate'], "%m/%d/%Y").strftime('%Y-%m-%d')
    endDate = datetime.strptime(rspFunctional['stuEndDate'], "%m/%d/%Y").strftime('%Y-%m-%d')
    # Creates the labor Status form
    lsf = LaborStatusForm.create(termCode_id = term,
                                 studentSupervisee_id = student.ID,
                                 supervisor_id = primarySupervisor,
                                 department_id  = department,
                                 jobType = rspFunctional["stuJobType"],
                                 WLS = rspFunctional["stuWLS"],
                                 POSN_TITLE = rspFunctional["stuPosition"],
                                 POSN_CODE = rspFunctional["stuPositionCode"],
                                 contractHours = rspFunctional.get("stuContractHours", None),
                                 weeklyHours   = rspFunctional.get("stuWeeklyHours", None),
                                 startDate = startDate,
                                 endDate = endDate,
                                 supervisorNotes = rspFunctional["stuNotes"],
                                 laborDepartmentNotes = rspFunctional["stuLaborNotes"],
                                 studentName = student.legal_name + " " + student.LAST_NAME,
                                 studentExpirationDate = calculateExpirationDate()
                                 )

    return lsf


def createOverloadFormAndFormHistory(rspFunctional, lsf, creatorID, host=None):
    """
    Creates a 'Labor Status Form' and then if the request needs an overload we create
    a 'Labor Overload Form'. Emails are sent based on whether the form is an 'Overload Form'
    rspFunctional: a dictionary containing all the data submitted in the LSF page
    lsf: stores the new instance of a labor status form
    creatorID: id of the user submitting the labor status form
    status: status of the labor status form (e.g. Pending, etc.)
    """
    # We create a 'Labor Status Form' first, then we check to see if a 'Labor Overload Form'
    # needs to be created
    try:
        isOverload = rspFunctional.get("isItOverloadForm") == "True"
        if isOverload:
            newLaborOverloadForm = OverloadForm.create( studentOverloadReason = None,
                                                        financialAidApproved = None,
                                                        financialAidApprover = None,
                                                        financialAidReviewDate = None,
                                                        SAASApproved = None,
                                                        SAASApprover = None,
                                                        SAASReviewDate = None,
                                                        laborApproved = None,
                                                        laborApprover = None,
                                                        laborReviewDate = None)
            formOverload = FormHistory.create( formID = lsf.laborStatusFormID,
                                                historyType = "Labor Overload Form",
                                                overloadForm = newLaborOverloadForm.overloadFormID,
                                                createdBy   = creatorID,
                                                createdDate = date.today(),
                                                status      = "Pre-Student Approval")
            email = emailHandler(formOverload.formHistoryID)
            link = makeThirdPartyLink("student", host, formOverload.formHistoryID)
            email.LaborOverLoadFormSubmitted(link)

        formHistory = FormHistory.create( formID = lsf.laborStatusFormID,
                            historyType = "Labor Status Form",
                            overloadForm = None,
                            createdBy   = creatorID,
                            createdDate = date.today(),
                            status      = "Pre-Student Approval")

        if not formHistory.formID.termCode.isBreak and not isOverload:
            email = emailHandler(formHistory.formHistoryID)
            email.laborStatusFormSubmitted()
        return formHistory
    except Exception as e:
        print("Error creating overload form:", e)
        raise 


def checkForSecondLSFBreak(termCode, student):
    """
    Checks if a student has more than one labor status form submitted for them during a break term, and sends emails accordingly.
    """
    positions = (LaborStatusForm.select()
                                .join(FormHistory)
                                .where( LaborStatusForm.termCode == termCode, 
                                        LaborStatusForm.studentSupervisee == student,
                                        ~(FormHistory.status_id % "Denied%"))
                                .distinct())
    isMoreLSFDict = {}
    storeLSFFormsID = []
    previousSupervisorNames = []
    if len(list(positions)) >= 1: # If student has one or more than one lsf
        isMoreLSFDict["showModal"] = True # show modal when the student has one or more than one lsf

        for item in positions:
            previousSupervisorNames.append(item.supervisor.FIRST_NAME + " " + item.supervisor.LAST_NAME)
            isMoreLSFDict["studentName"] = item.studentSupervisee.FIRST_NAME + " " + item.studentSupervisee.LAST_NAME
        isMoreLSFDict['previousSupervisorNames'] = previousSupervisorNames

        if len(list(positions)) == 1: # if there is only one labor status form then send email to the supervisor and student
            laborStatusFormID = positions[0].laborStatusFormID
            formHistoryID = FormHistory.get(FormHistory.formID == laborStatusFormID)
            isMoreLSFDict["formHistoryID"] = formHistoryID.formHistoryID

        else: # if there are more lsfs then send email to student, supervisor and all previous supervisors
            for item in positions: # add all the previous lsf ID's
                storeLSFFormsID.append(item.laborStatusFormID) # store all of the previous labor status forms for break
            laborStatusFormID = storeLSFFormsID.pop() #save all the previous lsf ID's except the one currently created. Pop removes the one created right now.
            formHistoryID = FormHistory.get(FormHistory.formID == laborStatusFormID)
            isMoreLSFDict['formHistoryID'] = formHistoryID.formHistoryID
            isMoreLSFDict["lsfFormID"] = storeLSFFormsID
    else:
        isMoreLSFDict["showModal"] = False # Do not show the modal when there's not previous lsf
    return json.dumps(isMoreLSFDict)

def checkForPrimaryPosition(termCode, student, currentUser):
    """ Checks if a student has a primary supervisor (which means they have primary position) in the selected term. """
    rsp = (request.data).decode("utf-8")  # This turns byte data into a string
    rspFunctional = json.loads(rsp)
    term = Term.get(Term.termCode == termCode)

    termYear = termCode[:-2]
    shortCode = termCode[-2:]
    clauses = []
    if shortCode == '00':
        fallTermCode = termYear + '11'
        springTermCode = termYear + '12'
        clauses.extend([FormHistory.formID.termCode == fallTermCode,
                        FormHistory.formID.termCode == springTermCode,
                        FormHistory.formID.termCode == termCode])
    else:
        ayTermCode = termYear + '00'
        clauses.extend([FormHistory.formID.termCode == ayTermCode,
                        FormHistory.formID.termCode == termCode])
    expression = reduce(operator.or_, clauses) # This expression creates SQL OR operator between the conditions added to 'clauses' list

    try:
        lastPrimaryPosition = FormHistory.select()\
                                         .join_from(FormHistory, LaborStatusForm)\
                                         .join_from(FormHistory, HistoryType)\
                                         .where((expression) &
                                                 (FormHistory.formID.studentSupervisee == student) &
                                                 (FormHistory.historyType.historyTypeName == "Labor Status Form") &
                                                 (FormHistory.formID.jobType == "Primary"))\
                                         .order_by(FormHistory.formHistoryID.desc())\
                                         .get()
    except DoesNotExist:
        lastPrimaryPosition = None

    if not lastPrimaryPosition:
        approvedRelease = None
    else:
        try:
            approvedRelease = FormHistory.select()\
                                         .where(FormHistory.formID == lastPrimaryPosition.formID,
                                                FormHistory.historyType == "Labor Release Form",
                                                FormHistory.status == "Approved")\
                                                .order_by(FormHistory.formHistoryID.desc())\
                                                .get()
        except DoesNotExist:
            approvedRelease = None

    finalStatus = {}
    if not term.isBreak:
        if lastPrimaryPosition and not approvedRelease:
            if rspFunctional == "Primary":
                if "Denied" in lastPrimaryPosition.status.statusName: # handle two denied statuses
                    finalStatus["status"] = "hire"
                else:
                    finalStatus["status"]  = "noHire"
                    finalStatus["term"] = lastPrimaryPosition.formID.termCode.termName
                    finalStatus["primarySupervisor"] = lastPrimaryPosition.formID.supervisor.FIRST_NAME + " " +lastPrimaryPosition.formID.supervisor.LAST_NAME
                    finalStatus["department"] = lastPrimaryPosition.formID.department.DEPT_NAME + " (" + lastPrimaryPosition.formID.department.ORG + "-" + lastPrimaryPosition.formID.department.ACCOUNT+ ")"
                    finalStatus["position"] = lastPrimaryPosition.formID.POSN_CODE +" - "+lastPrimaryPosition.formID.POSN_TITLE + " (" + lastPrimaryPosition.formID.WLS + ")"
                    finalStatus["hours"] = lastPrimaryPosition.formID.jobType + " (" + str(lastPrimaryPosition.formID.weeklyHours) + ")"
                    finalStatus["isLaborAdmin"] = currentUser.isLaborAdmin
                    finalStatus["approvedForm"] = (lastPrimaryPosition.status_id == "Approved")
            else:
                if lastPrimaryPosition.status_id in ["Approved", "Pending"]:
                    lastPrimaryPositionTermCode = str(lastPrimaryPosition.formID.termCode.termCode)[-2:]
                    # if selected term is AY and student has an approved/pending LSF in spring or fall
                    if shortCode == '00' and lastPrimaryPositionTermCode in ['11', '12']:
                        finalStatus["status"] = "noHireForSecondary"
                    else:
                        finalStatus["status"]  = "hire"
                else:
                    finalStatus["status"] = "noHireForSecondary"

        elif lastPrimaryPosition and approvedRelease:
            if rspFunctional == "Primary":
                finalStatus["status"]  = "hire"
            else:
                finalStatus["status"]  = "noHireForSecondary"
        else:
            if rspFunctional == "Primary":
                finalStatus["status"]  = "hire"
            else:
                finalStatus["status"]  = "noHireForSecondary"
    else:
        finalStatus["status"]  = "hire"
    return json.dumps(finalStatus)


def emailDuringBreak(secondLSFBreak, term):
    """
    Sending emails during break period
    """
    try: 
        if term.isBreak:
            isOneLSF = json.loads(secondLSFBreak)
            formHistory = FormHistory.get(FormHistory.formHistoryID == isOneLSF['formHistoryID'])
            email = emailHandler(formHistory.formHistoryID)
            email.laborStatusFormSubmitted()
            if(len(isOneLSF["previousSupervisorNames"]) > 1): #Student has more than one lsf. Send email to both supervisors and student
                email.notifyAdditionalLaborStatusFormSubmittedForBreak()
    except Exception as e:
        print("Error sending email during break:", e)
        raise
        


def createOverloadForm(newWeeklyHours, lsf, currentUser, adjustedForm=None,  formHistories=None, host=None):
    allTermForms = LaborStatusForm.select() \
                   .join_from(LaborStatusForm, Student) \
                   .join_from(LaborStatusForm, FormHistory) \
                   .where((LaborStatusForm.termCode == lsf.termCode) &
                         (LaborStatusForm.studentSupervisee.ID == lsf.studentSupervisee.ID) &
                         ~(FormHistory.status % "Denied%") &
                         (FormHistory.historyType == "Labor Status Form"))

    previousTotalHours = 0
    if allTermForms:
        for statusForm in allTermForms:
            previousTotalHours += statusForm.weeklyHours
    changeInHours = newWeeklyHours - lsf.weeklyHours
    newTotalHours = previousTotalHours + changeInHours

    if previousTotalHours <= 15 and newTotalHours > 15:  # If we weren't overloading and now we are
        newLaborOverloadForm = OverloadForm.create(studentOverloadReason = "None")
        newFormHistory = FormHistory.create(formID       = lsf.laborStatusFormID,
                                            historyType  = "Labor Overload Form",
                                            createdBy    = currentUser,
                                            adjustedForm = adjustedForm,
                                            overloadForm = newLaborOverloadForm.overloadFormID,
                                            createdDate  = date.today(),
                                            status       = "Pre-Student Approval")
        try:
            if formHistories:
                formHistories.status = "Pre-Student Approval"
                formHistories.save()

            else:
                modifiedFormHistory = FormHistory.select() \
                                    .join_from(FormHistory, HistoryType) \
                                    .where(FormHistory.formID == lsf.laborStatusFormID, FormHistory.historyType.historyTypeName == "Labor Status Form") \
                                    .get()
                modifiedFormHistory.status = "Pre-Student Approval"
                modifiedFormHistory.save()

            link = makeThirdPartyLink("student", host, newFormHistory.formHistoryID)
            overloadEmail = emailHandler(newFormHistory.formHistoryID)
            overloadEmail.LaborOverLoadFormSubmitted(link)

        except Exception as e:
            print("An error occured while attempting to send overload form emails: ", e)

    # This will delete an overload form after the hours are changed
    elif previousTotalHours > 15 and newTotalHours <= 15:  # If we were overloading and now we aren't
            print(f"Trying to get formhistory with formID '{lsf.laborStatusFormID}' and history type: 'Labor Overload Form'")
            # XXX this breaks if the overload was attached to a different form. ie, this form is the 
            #     primary, but a secondary is what triggered the overload process
            deleteOverloadForm = FormHistory.get((FormHistory.formID == lsf.laborStatusFormID) & (FormHistory.historyType == "Labor Overload Form"))
            deleteOverloadForm = OverloadForm.get(OverloadForm.overloadFormID == deleteOverloadForm.overloadForm_id)
            deleteOverloadForm.delete_instance()  # This line also deletes the Form History since it's set to cascade up in the model file
# end createOverloadForm
