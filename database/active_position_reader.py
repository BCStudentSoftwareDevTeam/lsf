import pandas as pd # Pandas library to allow for data manipulation and analysis in Python
from datetime import datetime
from app.models.laborStatusForm import *
from app.models.student import *
from app.models.department import *
import os.path
from app.logic.tracy import Tracy
from app.logic.userInsertFunctions import *

def convert_dept_org_act_to_id(row_data):
    """ Takes in the org and account number of current row of csv
        and returns the department ID for a LaborStatusForm """
    org_number, account_number = row_data.split("-")
    try:
        department = Department.get(Department.ACCOUNT == account_number, Department.ORG == org_number)
    except:
        tracy_departments = Tracy().getDepartments()
        for dept in tracy_departments:
            d, created = Department.get_or_create(DEPT_NAME = dept.DEPT_NAME, ACCOUNT = dept.ACCOUNT, ORG = dept.ORG)
            d.save()
        department = Department.get(Department.ACCOUNT == account_number, Department.ORG == org_number)
    return department.departmentID

def convert_dates_to_term_code(startDate, endDate):
    """ Takes in the start and end date from the current row of
        csv and returns them formatted for our database and also returns
        a term code """
    startDate = datetime.strptime(startDate, "%m/%d/%Y")
    endDate = datetime.strptime(endDate, "%m/%d/%Y")
    if datetime(endDate.year, 1, 1) <= endDate <= datetime(endDate.year, 5, 8):
        term_code = str(endDate.year) + "00"
        term_code = int(term_code) - 100 #if end date is in spring then change the term code based on the date
    else:
        term_code = str(endDate.year) + "00"
        term_code = int(term_code) #else make the term code with the year of the end date
    return startDate, endDate, term_code

labor_data = pd.read_csv("active_jobs_as_of_3-24-22.csv") #replace this with future labor data csv

production_bnumbers_list = []
production_forms = LaborStatusForm.select().where(LaborStatusForm.termCode_id == 202112 or LaborStatusForm.termCode_id == 202100 or LaborStatusForm.termCode_id == 202101 or LaborStatusForm.termCode_id == 202102 or LaborStatusForm.termCode_id == 202103).order_by(LaborStatusForm.studentSupervisee.asc())
for form in production_forms:
    production_bnumbers_list.append(str(form.studentSupervisee.ID))

created_forms = 0
updated_primaries = 0
updated_secondaries = 0
updated_second_secondaries = 0

for row in range(len(labor_data)):
    #wait = input("Waiting")
    #print(f"Processing position {labor_data.loc[row, 'Position']} for {labor_data.loc[row, 'First Name']} {labor_data.loc[row, 'Last Name']} ({labor_data.loc[row, 'B#']})")
    createSupervisorFromTracy(bnumber=labor_data.loc[row, "Supervisor B#"])
    dept_ID = convert_dept_org_act_to_id(labor_data.loc[row, "Dept Org and Account"])
    start_date, end_date, term_code = convert_dates_to_term_code(labor_data.loc[row, "Begin Date"], labor_data.loc[row, "End Date"])
    if labor_data.loc[row, "B#"] in production_bnumbers_list:
        if labor_data.loc[row, "Contract Type"] == "Primary": #if form does exist, check if primary and update
            update_stmt = LaborStatusForm.update(supervisor_id = labor_data.loc[row, "Supervisor B#"],
                                    department_id = dept_ID,
                                    WLS = labor_data.loc[row, "WLS"],
                                    POSN_TITLE = labor_data.loc[row, "Title"],
                                    POSN_CODE = labor_data.loc[row, "Position"],
                                    weeklyHours   = labor_data.loc[row, "Hours per Week"],
                                    startDate = start_date,
                                    endDate = end_date,
                                    studentName = labor_data.loc[row, "First Name"] + " " + labor_data.loc[row, "Last Name"]
                                    ).where((LaborStatusForm.studentSupervisee_id == labor_data.loc[row, "B#"]) & (LaborStatusForm.jobType == "Primary") & (LaborStatusForm.termCode_id == term_code))
            print(update_stmt)
            update_stmt.execute()
            updated_primaries += 1
            print("Updating Existing Primary Form")
            print(labor_data.loc[row, "Last Name"])
        elif labor_data.loc[row, "Contract Type"] == "Secondary": #if form does exist, check if secondary and update
            bnumber=labor_data.loc[row, "B#"]
            title=labor_data.loc[row, "Title"]
            print("Updating First Secondary")
            print(labor_data.loc[row, "Last Name"])
            LaborStatusForm.update(supervisor_id = labor_data.loc[row, "Supervisor B#"],
                                    department_id = dept_ID,
                                    WLS = labor_data.loc[row, "WLS"],
                                    POSN_TITLE = title,
                                    POSN_CODE = labor_data.loc[row, "Position"],
                                    weeklyHours   = labor_data.loc[row, "Hours per Week"],
                                    startDate = start_date,
                                    endDate = end_date,
                                    studentName = labor_data.loc[row, "First Name"] + " " + labor_data.loc[row, "Last Name"]
                                    ).where((LaborStatusForm.studentSupervisee_id == bnumber) & (LaborStatusForm.jobType == "Secondary") & (LaborStatusForm.POSN_TITLE == title) & (LaborStatusForm.termCode_id == term_code)).execute()
            updated_secondaries += 1
            for new_row in range(len(labor_data)): #Loop through again looking for a second secondary and update if found
                new_dept_ID = convert_dept_org_act_to_id(labor_data.loc[new_row, "Dept Org and Account"]) #Need new dept ID for this loop
                new_start_date, new_end_date, new_term_code = convert_dates_to_term_code(labor_data.loc[new_row, "Begin Date"], labor_data.loc[new_row, "End Date"]) #Need new term code and dates for this loop
                if labor_data.loc[new_row, "Contract Type"] == "Secondary" and labor_data.loc[new_row, "B#"] == bnumber and labor_data.loc[new_row, "Title"] != title:
                    print("Updating Second Secondary")
                    print(labor_data.loc[new_row, "Last Name"])
                    LaborStatusForm.update(supervisor_id = labor_data.loc[new_row, "Supervisor B#"],
                                            department_id = new_dept_ID,
                                            WLS = labor_data.loc[new_row, "WLS"],
                                            POSN_TITLE = labor_data.loc[new_row, "Title"],
                                            POSN_CODE = labor_data.loc[new_row, "Position"],
                                            weeklyHours   = labor_data.loc[new_row, "Hours per Week"],
                                            startDate = new_start_date,
                                            endDate = new_end_date,
                                            studentName = labor_data.loc[new_row, "First Name"] + " " + labor_data.loc[new_row, "Last Name"]
                                            ).where((LaborStatusForm.studentSupervisee_id == labor_data.loc[new_row, "B#"]) & (LaborStatusForm.jobType == "Secondary") & (LaborStatusForm.POSN_TITLE == title) & (LaborStatusForm.termCode_id == new_term_code)).execute()
                    updated_second_secondaries += 1

for row in range(len(labor_data)): #Looping through the current forms
    print(labor_data.loc[row, "First Name"] + labor_data.loc[row, "Last Name"])
    createSupervisorFromTracy(bnumber=labor_data.loc[row, "Supervisor B#"])
    dept_ID = convert_dept_org_act_to_id(labor_data.loc[row, "Dept Org and Account"])
    start_date, end_date, term_code = convert_dates_to_term_code(labor_data.loc[row, "Begin Date"], labor_data.loc[row, "End Date"])
    if labor_data.loc[row, "B#"] not in production_bnumbers_list: #if bnumber doesn't exist try to get/create student record and then create a new form
        try:
            getOrCreateStudentRecord(bnumber = labor_data.loc[row, "B#"])
        except:
            print("creating student record from scratch")
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
        LaborStatusForm.create(termCode_id = term_code,
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
        created_forms += 1
        print("Created labor status form for", labor_data.loc[row, "B#"])


print("Number of New Forms:", created_forms)
print("Number of Updated Primaries:", updated_primaries)
print("Number of Updated Secondaries:", updated_secondaries)
print("Number of Updated Second Secondaries:", updated_second_secondaries)
