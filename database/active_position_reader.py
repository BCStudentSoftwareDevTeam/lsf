import pandas as pd # Pandas library to allow for data manipulation and analysis in Python
import csv
from app.models.laborStatusForm import *
from app.models.student import *
from app.models.department import *
import os.path
from app.logic.tracy import Tracy
from app.logic.userInsertFunctions import *

# if not os.path.exists("active_jobs_as_of_2-18-22_new.csv"):
#     current_positions_file = pd.read_excel("active_jobs_as_of_2-18-22_new.xlsx")
#     current_positions_file.to_csv("active_jobs_as_of_2-18-22_new.csv",
#                                   index = None,
#                                   header = True)

# labor_data = pd.read_csv("active_jobs_as_of_2-18-22_new.csv")
# position_title_list = labor_data["Title"].tolist()
# position_title_list.sort()

# production_position_titles = []
# current_labor_forms = LaborStatusForm.select().order_by(LaborStatusForm.POSN_TITLE.asc())
# for form in current_labor_forms:
#     production_position_titles.append(form.POSN_TITLE)
#
# POSN_TITLE_differences_list = []
# for title in position_title_list:
#     if title not in production_position_titles:
#         POSN_TITLE_differences_list.append(title)
# print(POSN_TITLE_differences_list)

# def convert_dept_org_act_to_id(row_data):
#     org_number, account_number = row_data.split("-")
#     dept = Department.get(Department.ORG==org_number, Department.ACCOUNT==account_number)
#     return dept.departmentID

def convert_end_date_to_term_code(date):
    term_code = date[4:]


labor_data = pd.read_csv("active_jobs_as_of_3-24-22.csv")
position_name_list = labor_data["B#"].tolist()
position_name_list.sort()

production_bnumbers_list = []
# production_names = LaborStatusForm.select().join(Student).order_by(LaborStatusForm.studentSupervisee.LAST_NAME.asc())
production_forms = LaborStatusForm.select().order_by(LaborStatusForm.studentSupervisee.asc())
for form in production_forms:
    production_bnumbers_list.append(form.studentSupervisee)

for row in range(len(labor_data)):
    if labor_data.loc[row, "B#"] not in production_bnumbers_list:
        try:
            getOrCreateStudentRecord(None, labor_data.loc[row, "B#"])
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
        createSupervisorFromTracy(None, labor_data.loc[row, "Supervisor B#"])
        dept_ID = convert_dept_org_act_to_id(labor_data.loc[row, "Dept Org and Account"])
        LaborStatusForm.create(termCode_id = 201511,
                                studentSupervisee_id = labor_data.loc[row, "B#"],
                                supervisor_id = labor_data.loc[row, "Supervisor B#"],
                                department_id = dept_ID,
                                jobType = labor_data.loc[row, "Contract Type"],
                                WLS = labor_data.loc[row, "WLS"],
                                POSN_TITLE = labor_data.loc[row, "Title"],
                                POSN_CODE = labor_data.loc[row, "Position"],
                                contractHours = None,
                                weeklyHours   = labor_data.loc[row, "Hours per Week"],
                                startDate = None,
                                endDate = None,
                                supervisorNotes = None,
                                laborDepartmentNotes = None,
                                studentName = labor_data.loc[row, "First Name"] + " " + labor_data.loc[row, "Last Name"]
                                )
