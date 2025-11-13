import csv
import re
from app.models.term import Term
from app.models.student import Student
from app.logic.userInsertFunctions import *
import random
import dateutil.parser
from datetime import timedelta


DEBUG=False

def debug(msg):
    if DEBUG:
        print(msg)


def getReader(f, fields):
    reader = csv.DictReader(f, delimiter=',', fieldnames=fields, restkey='extra', restval='XXXX')
    reader.__next__() # skip header

    return reader

def getList(f, fields):
    reader = getReader(f, fields)
    return [row for row in reader]

def validate_file(f, fields):
    reader = getReader(f, fields)
    success = True

    # Check for places where we didn't escape text
    for row in reader:
        if 'extra' in row and row['extra'] is not None:
            print("Line {}:".format(reader.line_num), "Extra comma in line. Need quotes")
            success = False

        try:
            int(row['form_id'])
            if row['note'] == 'XXXX': # XXX breaks on the last line
                print("Line {}:".format(reader.line_num), "Not enough columns")
                success = False
        except:
            print("Line {}:".format(reader.line_num), "Bad ID '{}'. Need quotes on previous line.".format(row['form_id']))
            success = False

    f.seek(0)

    return success

def getTerm(raw_term, start_year, terms):

    termname = raw_term.strip()

    # massage term names to our old terms
    if termname == "Summer Break":
        termname = "Summer"
    elif "Spring Break 2016" in termname:
        termname = "Spring Break 2016"
    elif "Summer 2016" in termname:
        termname = "Summer 2016"
    elif "Fall Term 2017" in termname:
        termname = "Fall 2017"
    elif "Winter 2017" in termname:
        termname = "Christmas Break 2017"
    elif "Winter 2018" in termname:
        termname = "Christmas Break 2018"
    elif "for Closure" in termname:
        termname = "Spring COVID-19 Closure 2020"

    # there are Christmas Break 2019s with start dates in 2020, we want to keep 2019
    match = re.search(r'\d\d\d\d', termname)
    if match and match.group() != start_year:
        pass
    # If the term doesn't have a year on it, add it
    elif start_year not in termname:
        termname += " {}".format(start_year)

    if start_year not in terms:
        terms[start_year] = {}
    if termname not in terms[start_year]:
        terms[start_year][termname] = None

    term = Term.get(Term.termName == termname)
    terms[start_year][termname] = term.termCode

    return term

def guessEmailAndName(raw_name):
    email_guess, first_name, last_name = 'Unknown','Unknown','From Old System'
    if raw_name:
        name = raw_name.split(' ')
        first_name = name[0]
        if len(name) > 1:
            last_name = " ".join(name[1:])
        else:
            last_name = ""

        if first_name:
            email_guess = last_name.lower() + first_name[0] + "@berea.edu"

    return email_guess, first_name, last_name

def handleSupervisor(raw_id, raw_name, department):
    id_text = raw_id.strip()

    try:
        supervisor = (Supervisor.get_or_none(ID=id_text) or
                     createSupervisorFromTracy(bnumber=id_text))
        debug("Found {} as a supervisor".format(supervisor.FIRST_NAME + " " + supervisor.LAST_NAME))
    except InvalidUserException:
        debug("Can't find a matching supervisor for {}".format(id_text))

        # We have to create a supervisor, but we don't have their data from Tracy, just name and bnumber
        email_guess, first_name, last_name = guessEmailAndName(raw_name)

        supervisor = Supervisor.create(
                ID=id_text,
                FIRST_NAME=first_name,
                LAST_NAME=last_name,
                EMAIL=email_guess,
                CPO="Unknown",
                ORG="Unknown",
                DEPT_NAME=department.DEPT_NAME
                )

    return supervisor

def handleStudent(raw_student, raw_name):
    id_text = raw_student.strip()
    try:
        student = Student.get_or_none(ID=id_text)
        if not student:
            obj = Tracy().getStudentFromBNumber(id_text)
            student = createStudentFromTracyObj(obj)
        debug("Found {} as a student".format(str(student.FIRST_NAME) + " " + str(student.LAST_NAME)))
    except (InvalidQueryException, InvalidUserException):
        debug("Can't find a matching student for {}".format(id_text))

        # We have to create a student, but we don't have their data from Tracy, just name and bnumber
        email_guess, first_name, last_name = guessEmailAndName(raw_name)
        student = Student.create(
                ID=id_text,
                FIRST_NAME=first_name,
                LAST_NAME=last_name,
                STU_EMAIL=email_guess,
                STU_CPO="Unknown"
                )

    return student

# Create User and Student/Supervisor records based on username
def userFromUsername(username, department):
    if username == "":
        return None

    user, created = User.get_or_create(username=username)
    if created:
        supervisor, student = None, None
        try:
            supervisor = createSupervisorFromTracy(username=username)
        except InvalidUserException:
            try:
                student = createStudentFromTracy(username)
            except InvalidUserException:
                # Make a mostly blank supervisor from username
                fakeid = "B99" + str(random.randint(100000,999999))
                supervisor = Supervisor.create(
                        ID=fakeid,
                        FIRST_NAME="Unknown",
                        LAST_NAME="User (from old LSF)",
                        EMAIL=(username + "@berea.edu"),
                        CPO="Unknown",
                        ORG="Unknown",
                        DEPT_NAME=department.DEPT_NAME
                        )

        user.student = student
        user.supervisor = supervisor
        user.save()

    return user


def importRecord(record, terms):
    debug(record)

    try:
        # There won't be positions for the old stuff, but that's ok because we have all the data
        position = Tracy().getPositionFromCode(record['posn_code'])
    except InvalidQueryException:
        if 'department' not in record:
            print("There is no position code {} in Tracy and we need it for department".format(record['posn_code']))
            return False


    # Populate department table
    if 'department' in record:
        department,created = Department.get_or_create(
            DEPT_NAME=record['department'],
            ACCOUNT=record['departmentAccount'],
            ORG=record['departmentCode'])
    else:
        department,created = Department.get_or_create(
            DEPT_NAME=position.DEPT_NAME,
            ACCOUNT=position.ACCOUNT,
            ORG=position.ORG)

    if department.DEPT_NAME.strip() == "":
        debug("XXX Don't save records with the empty department")
        return False

    if record['posn_code'] == "S12345":
        debug("XXX Don't save the DUMMY position code")
        return False


    # Ensure Supervisor record exists
    name = record['supervisorName'] if 'supervisorName' in record else ''
    supervisor = handleSupervisor(record['supervisor'], name, department)

    # Ensure Student record exists
    name = record['superviseeName'] if 'superviseeName' in record else ''
    student = handleStudent(record['supervisee'], name)

    # Set up Terms
    try:
        term = getTerm(record['term'], record['start'].split('-')[0], terms)
    except DoesNotExist:
        print("XXX Can't find a matching term for '{}'".format(record['term']))
        return False

    # estimate the proper hours and length of the contract
    weeks = 16
    if term.isSummer:
        weeks = 8
    elif term.isBreak:
        weeks = 1
        if 'Christmas' in term.termName:
            weeks = 4

    weekly_hours = record['hour']
    contract_hours = None

    if weeks < 16:
        if int(record['hour']) <= 10:
            contract_hours = int(record['hour']) * 5 * weeks
        elif 10 < int(record['hour']) <= 20:
            contract_hours = int(record['hour']) * weeks
        else:
            contract_hours = int(record['hour'])
        weekly_hours = None
    
    end_date = record['end'].strip()
    if end_date == '':
        end_date = dateutil.parser.isoparse(record['start']) + timedelta(weeks=weeks)



    form = LaborStatusForm.create(
        studentName=student.FIRST_NAME + " " + student.LAST_NAME,
        termCode=term.termCode,
        studentSupervisee=student.ID,
        supervisor=supervisor.ID,
        department=department.departmentID,
        jobType='Primary' if record['job_type'] == 'Primary' else 'Secondary',
        WLS=record['WLS'] if 'WLS' in record else position.WLS,
        POSN_TITLE=record['positionName'] if 'positionName' in record else position.POSN_TITLE,
        POSN_CODE=record['posn_code'],
        contractHours=contract_hours,
        weeklyHours=weekly_hours,
        startDate=record['start'],
        endDate=end_date,
        laborDepartmentNotes=record['note'])

    creator = userFromUsername(record['creator'], department)
    status = Status.get(Status.statusName == "Pending")

    create_date = record['start']
    if 'created_on' in record and record['created_on'] != "":
        create_date = record['created_on']
    create_date = dateutil.parser.isoparse(create_date[:-3]) # we have extra fractional zeroes for some reason

    historyType = HistoryType.get(HistoryType.historyTypeName == "Labor Status Form")
    fh_entry = FormHistory.create(
            formID = form.laborStatusFormID,
            historyType = historyType.historyTypeName,
            createdBy = creator,
            createdDate = create_date,
            status = status.statusName)

    # Create rejected form or approval
    if 'approval' in record:
        if record['approval'] == "1":
            status = Status.get(Status.statusName == "Approved")

        elif record['approval'] == "-1":
            status = Status.get(Status.statusName == "Denied")
            fh_entry.rejectReason = record['rejectReason']

        processor = userFromUsername(record['processedBy'], department)
        if not processor:
            processor = creator
            processed_date = create_date
        else:
            processed_date = dateutil.parser.parse(timestr=record['processedDate'])

        fh_entry.reviewedBy = processor
        fh_entry.reviewedDate = processed_date
        fh_entry.status = status.statusName

        fh_entry.save()

    debug("Saved.")
    return True
