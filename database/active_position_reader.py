import pandas as pd # Pandas library to allow for data manipulation and analysis in Python
from datetime import datetime, timedelta
from app.models.laborStatusForm import *
from app.models.student import *
from app.models.department import *
import os.path
from app.logic.tracy import Tracy
from app.logic.userInsertFunctions import *
from app.models import mainDB
from peewee import DoesNotExist

def get_all_departments():
    """ Add any new departments from Tracy that we don't have """
    for dept in Tracy().getDepartments():
        try:
            Department.get(Department.DEPT_NAME == dept.DEPT_NAME, Department.ACCOUNT == dept.ACCOUNT, Department.ORG == dept.ORG)
        except DoesNotExist as e:
            update_rows = Department.update(DEPT_NAME = dept.DEPT_NAME).where(Department.ACCOUNT == dept.ACCOUNT, Department.ORG == dept.ORG).execute()
            if update_rows:
                print(f"  Updated department from Tracy: {dept.DEPT_NAME}, {dept.ACCOUNT}, {dept.ORG}")
            else:
                Department.create(DEPT_NAME = dept.DEPT_NAME, ACCOUNT = dept.ACCOUNT, ORG = dept.ORG)
                print(f"  Created new department from Tracy: {dept.DEPT_NAME}, {dept.ACCOUNT}, {dept.ORG}")


def convert_dept_org_act_to_id(row_data):
    """ Takes in the org and account number of current row of csv
        and returns the department ID for a LaborStatusForm """
    org_number, account_number = row_data.split("-")
    return Department.get(Department.ACCOUNT == account_number, Department.ORG == org_number)

def convert_dates_to_term_code(startDate, endDate):
    """ Takes in the start and end date from the current row of
        csv and returns them formatted for our database and also returns
        the correct Academic Year term code """
    startDate = datetime.strptime(startDate, "%m/%d/%Y")
    endDate = datetime.strptime(endDate, "%m/%d/%Y")
    term_code = int(str(endDate.year) + "00")
    if datetime(endDate.year, 1, 1) <= endDate <= datetime(endDate.year, 5, 8):
        term_code -= 100 #if end date is in spring then correct the term code

    return startDate, endDate, term_code

def supervisor_to_user(bnumber):
    try:
        return User.get(supervisor_id=bnumber)
    except:
        print("  Uhoh, no user for this supervisor. This will cause an error in creation.", bnumber)

def update_record(form, row):
    start_date, end_date, term_code = convert_dates_to_term_code(labor_data.loc[row, "Begin Date"], labor_data.loc[row, "End Date"])
    dept_ID = convert_dept_org_act_to_id(labor_data.loc[row, "Dept Org and Account"]) 

    form.supervisor_id = labor_data.loc[row, "Supervisor B#"]
    form.department_id = dept_ID
    form.WLS = labor_data.loc[row, "WLS"]
    form.POSN_TITLE = labor_data.loc[row, "Title"]
    form.POSN_CODE = labor_data.loc[row, "Position"]
    form.weeklyHours   = labor_data.loc[row, "Hours per Week"]
    form.startDate = start_date
    form.endDate = end_date
    form.studentName = labor_data.loc[row, "First Name"] + " " + labor_data.loc[row, "Last Name"]
    form.termCode_id = term_code
    form.save()

def create_record(row):
    start_date, end_date, term_code = convert_dates_to_term_code(labor_data.loc[row, "Begin Date"], labor_data.loc[row, "End Date"])
    dept_ID = convert_dept_org_act_to_id(labor_data.loc[row, "Dept Org and Account"]) 
    supervisor = supervisor_to_user(labor_data.loc[row, "Supervisor B#"])

    # create
    with mainDB.atomic() as transaction:
        lsf = LaborStatusForm.create(termCode_id = term_code,
                                studentSupervisee_id = labor_data.loc[row, "B#"],
                                supervisor_id = labor_data.loc[row, "Supervisor B#"],
                                department_id = dept_ID,
                                jobType = labor_data.loc[row, "Contract Type"],
                                WLS = labor_data.loc[row, "WLS"],
                                POSN_TITLE = labor_data.loc[row, "Title"],
                                POSN_CODE = labor_data.loc[row, "Position"],
                                contractHours = None,
                                weeklyHours   = labor_data.loc[row, "Hours per Week"],
                                startDate = start_date,
                                endDate = end_date,
                                supervisorNotes = None,
                                laborDepartmentNotes = None,
                                studentName = labor_data.loc[row, "First Name"] + " " + labor_data.loc[row, "Last Name"]
                                )
        FormHistory.create(formID=lsf, 
                           historyType="Labor Status Form", 
                           createdBy=supervisor,
                           createdDate=start_date - timedelta(days=2),
                           reviewedDate=start_date - timedelta(days=1),
                           reviewedBy=supervisor,
                           status_id='Approved')
    return lsf
        
def print_banner_row(row):
    print(labor_data.loc[row,:])



###########################################################################################
### BEGIN ###
###########################################################################################
labor_data = pd.read_csv("active_jobs.csv")

secondary_indexes = {} # store the secondary position indexes for each B# 
primary_indexes = {}  # store the primary position indexes for each B# 
supervisor_cache = {}

print("Updating departments...")
get_all_departments()

# initial pass, ensuring supervisors and students are in our database and collating student records
print("Initial pass through the data...")
for row in range(len(labor_data)):

    # clean some data. try not to repeat queries
    try:
        supervisor_cache[labor_data.loc[row, "Supervisor B#"]]
    except:
        createSupervisorFromTracy(bnumber=labor_data.loc[row, "Supervisor B#"])
        supervisor_cache[labor_data.loc[row, "Supervisor B#"]] = 1

    # make sure we have a student record
    try:
        # try to get from Tracy if we need to
        getOrCreateStudentRecord(bnumber = labor_data.loc[row, "B#"])
    except:
        print(f"Creating student record from scratch ({labor_data.loc[row, 'B#']})")
        Student.create(ID = labor_data.loc[row, "B#"],
                        PIDM = None,
                        FIRST_NAME = labor_data.loc[row, "First Name"],
                        LAST_NAME = labor_data.loc[row, "Last Name"],
                        CLASS_LEVEL = None,
                        ACADEMIC_FOCUS = None,
                        MAJOR = None,
                        PROBATION = None,
                        ADVISOR = None,
                        STU_EMAIL = None,
                        STU_CPO = None,
                        LAST_POSN = None,
                        LAST_SUP_PIDM = None
                        )

    # collect records by bnumber
    if labor_data.loc[row, 'Contract Type'] == 'Secondary':
        secondary_indexes.setdefault(labor_data.loc[row, 'B#'], []).append(row)
    elif labor_data.loc[row, 'Contract Type'] == 'Primary':
        primary_indexes.setdefault(labor_data.loc[row, 'B#'], []).append(row)
    else:
        # unknown value
        print(f"Unknown Contract Type!! {labor_data.loc[row, 'Contract Type']}")
        quit()
# End csv loop

created_primaries = 0
created_secondaries = 0
updated_primaries = 0
updated_secondaries = 0
updated_second_secondaries = 0

###########################################################################################
### Primaries ###
###########################################################################################
print()
print("Processing Primary Records")
print("--------------------------")
for student_id, banner_forms in primary_indexes.items():
    print()
    print(f"Processing {student_id}")

    lsf_forms = (LaborStatusForm.select().where(
                                (LaborStatusForm.studentSupervisee_id == student_id) & 
                                (LaborStatusForm.jobType == 'Primary') & 
                                (LaborStatusForm.termCode_id << [202112,202111,202100]) # current AY
                            ).order_by(LaborStatusForm.laborStatusFormID.desc())) # ordering to facilitate updates
    lsf_count = len(lsf_forms)
    banner_count = len(banner_forms)

    # sanity check
    if banner_count > 1:
        print("  I didn't think there were multiple banner primaries.", labor_data.loc[row, "B#"])
        quit()

    row = banner_forms[0] # only one record to deal with for primaries

    # create
    if banner_count and not lsf_count:
        lsf = create_record(row)
        created_primaries += 1
        print(f"  Created Primary labor status form {lsf.laborStatusFormID} for {labor_data.loc[row, 'B#']}")

    # update
    else:
        if lsf_count > 1:
            print("  This student had multiple primaries. Check to make sure the proper one was updated.")

        # only update the most recent one, to handle one in banner and 2 in lsf
        most_recent_form = lsf_forms.get()
        update_record(most_recent_form, row)

        print(f"  Updated Primary labor status form {most_recent_form.laborStatusFormID} for {labor_data.loc[row, 'B#']}.")
        updated_primaries += 1
        

"""
Data stats

Checking Primary records for this academic year (Fall, Spring, AY) for each student
One record in both: 1121
Same record counts in both (>1): 0
Not in LSF but in Banner: 1
In LSF but not in Banner: 0
More records in Banner (excluding above): 0
More records in LSF (excluding above): 170

Checking Secondary records for this academic year (Fall, Spring, AY) for each student
One record in both: 223
Same record counts in both (>1): 5
Not in LSF but in Banner: 4
In LSF but not in Banner: 0
More records in Banner (excluding above): 1
More records in LSF (excluding above): 37
"""


manual_records = {}

###########################################################################################
### Secondaries ###
###########################################################################################
print()
print("Processing Secondary Records")
print("--------------------------")
for student_id, banner_forms in secondary_indexes.items():
    print()
    print(f"Processing {student_id}")

    lsf_forms = (LaborStatusForm.select().where(
                                (LaborStatusForm.studentSupervisee_id == student_id) & 
                                (LaborStatusForm.jobType == 'Secondary') & 
                                (LaborStatusForm.termCode_id << [202112,202111,202100]) # current AY
                            ).order_by(LaborStatusForm.laborStatusFormID.desc())) # ordering to facilitate updates

    lsf_count = len(lsf_forms)
    banner_count = len(banner_forms)

    # one to one match 
    # (unless something weird happened where one in lsf was rejected and there's a totally different one in banner?)
    if lsf_count == 1 and banner_count == 1:
        update_record(lsf_forms.get(), banner_forms[0])
        updated_secondaries += 1
        print("  Updating Secondary Form")
        
    # we need to match up the secondaries to update the correct ones
    elif lsf_count == banner_count:

        # hardcoded fixes
        if student_id in ["B00763542", "B00759095"]:
            update_record(list(lsf_forms)[0], banner_forms[0])
            update_record(list(lsf_forms)[1], banner_forms[1])

        elif student_id in ["B00750058","B00709946","B00750760"]:
            update_record(list(lsf_forms)[0], banner_forms[1])
            update_record(list(lsf_forms)[1], banner_forms[0])

        else:
            print("  XXX Even counts in LSF and Banner. Need to match them up manually, to be safe.")
            print(list(lsf_forms))
            for row in banner_forms:
                print_banner_row(row)


    # new secondaries
    elif lsf_count == 0 and banner_count > 0:
        for row in banner_forms:
            lsf = create_record(row)
            created_secondaries += 1
            print(f"  Created new Secondary form {lsf.laborStatusFormID}")

    #an extra secondary in banner to create
    elif banner_count > lsf_count:

        # hardcode this fix
        if student_id in ["B00730368"]:
            update_record(list(lsf_forms)[0], banner_forms[0])
            create_record(banner_forms[1])

        else:
            print("  XXX Extra Secondaries in Banner for Unknown Student. Resolve them manually, to be safe.")
            print(lsf_forms)
            for row in banner_forms:
                print_banner_row(row)
        

    #extra secondaries in lsf 
    else:
        # we can't just update the most recent. Doesn't work for B00773583, B00762761, at least
        print(f"  XXX Extra Secondaries in LSF. Saving resolution for later")
        manual_records[student_id] = banner_forms


print()
print("Number of New Primaries:", created_primaries)
print("Number of Updated Primaries:", updated_primaries)
print("Number of New Secondaries:", created_secondaries)
print("Number of Updated Secondaries:", updated_secondaries)
print("Number of Updated Second Secondaries:", updated_second_secondaries)

for student_id, banner_forms in manual_records.items():
    print()
    print("-------------------------------------------------------------------")
    print(student_id)
    print("-------------------------------------------------------------------")
    for row in banner_forms:
        print_banner_row(row)
        print("-------------------------------------------------------------------")

