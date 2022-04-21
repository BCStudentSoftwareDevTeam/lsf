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

def print_banner_row(row):
    print(labor_data.loc[row,:])




###########################################################################################
### BEGIN ###
###########################################################################################
labor_data = pd.read_csv("active_jobs.csv")

rows_to_process = {
        68: 33746,
        72: 33608,
        171: 32925,
        172: 32791,
        187: 33999,
        284: 33785,
        288: 33826,
        299: 33901,
        375: 33819,
        477: 32706,
        478: 32704,
        908: 32964,
        515: 33595,
        518: 33123,
        522: 33700,
        533: 33044,
        593: 34278,
        652: 33078,
        653: 33174,
        656: 34028,
        658: 33750,
        666: 32913,
        848: 33768,
        1126: 33783,
        881: 32759,
        907: 33850,
        916: 33713,
        918: 33881,
        1074: 33617,
        1076: 33831,
        1111: 33736,
        1393: 33198,
        1112: 33680,
        1113: 33719,
        1127: 32058,
        1192: 33043,
        1283: 33129,
        1465: 33296,
        1466: 33592,
        1543: 34188
}

print()
print("Processing Secondary Records")
print("--------------------------")
for row, lsf_id in rows_to_process.items():
    print()
    form = LaborStatusForm.get_by_id(lsf_id);
    print(f"Processing {form.studentSupervisee_id}")
    if form.studentSupervisee_id != labor_data.loc[row,'B#']:
        print("Mismatched Record!", form.studentSupervisee_id, labor_data.loc[row,'B#'])
        quit()

    update_record(form, row)

