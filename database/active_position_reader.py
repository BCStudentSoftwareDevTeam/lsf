import pandas as pd # Pandas library to allow for data manipulation and analysis in Python
import csv
from app.models.laborStatusForm import *
import os.path
from app.logic.tracy import Tracy
from app.logic.userInsertFunctions import createStudentFromTracy

if not os.path.exists("active_jobs_as_of_2-18-22_new.csv"):
    current_positions_file = pd.read_excel("active_jobs_as_of_2-18-22_new.xlsx")
    current_positions_file.to_csv("active_jobs_as_of_2-18-22_new.csv",
                                  index = None,
                                  header = True)

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

labor_data = pd.read_csv("active_jobs_as_of_2-18-22_new.csv")
position_name_list = labor_data["B#"].tolist()
position_name_list.sort()

production_names_list = []
# production_names = LaborStatusForm.select().join(Student).order_by(LaborStatusForm.studentSupervisee.LAST_NAME.asc())
production_names = LaborStatusForm.select().order_by(LaborStatusForm.studentSupervisee.asc())
for name in production_names:
    production_names_list.append(name.studentSupervisee)

for row in range(len(labor_data)):
    if labor_data.loc[row, "B#"] not in production_names_list:
        createStudentFromTracy(None, labor_data.loc[row, "B#"])
        LaborStatusForm.create(termCode_id = 201511,
                                studentSupervisee_id = labor_data.loc[row, "B#"],
                                supervisor_id = labor_data.loc[row, "Supervisor B#"],
                                department_id  = 2,
                                jobType = labor_data.loc[row, "Contract Type"],
                                WLS = labor_data.loc[row, "WLS"],
                                POSN_TITLE = labor_data.loc[row, "Title"],
                                POSN_CODE = labor_data.loc[row, "Position"],
                                contractHours = None,
                                weeklyHours   = labor_data.loc[row, "Hours per Week"],
                                startDate = labor_data.loc[row, "Begin Date"],
                                endDate = labor_data.loc[row, "End Date"],
                                supervisorNotes = None,
                                laborDepartmentNotes = None,
                                studentName = labor_data.loc[row, "First Name"] + labor_data.loc[row, "Last Name"]
                                )
        print(labor_data.loc[row, "B#"])

for row in range(len(labor_data)):
    if labor_data.loc[row, "B#"] not in production_names_list:
        print(labor_data.loc[row, "B#"])
        # LaborStatusForm.delete().where(termCode_id = 201511,
        #                                studentSupervisee_id = row["B#"],
        #                                supervisor_id = row["Supervisor B#"],
        #                                department_id  = 2,
        #                                jobType = row["Contract Type"],
        #                                WLS = row["WLS"],
        #                                POSN_TITLE = row["Title"],
        #                                POSN_CODE = row["Position"],
        #                                contractHours = None,
        #                                weeklyHours   = row["Hours per Week"],
        #                                startDate = row["Begin Date"],
        #                                endDate = row["End Date"],
        #                                supervisorNotes = None,
        #                                laborDepartmentNotes = None,
        #                                studentName = row["First Name"] + row["Last Name"]
        #                                )
