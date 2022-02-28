import csv
import xlrd
import pandas as pd

current_positions_file = xlrd.open_workbook("active_jobs_as_of_2-18-22_new.xlsx").sheet_by_index(0)
writer = csv.writer(open("active_jobs_2022.csv",
                         'w',
                         newline=""))

for row in range(current_positions_file.nrows):
    writer.writerow(shee.row_values(row))

active_positions = open("fix-fall-positions/activepositions.csv")
read_positions_file = csv.reader(active_positions)

header = []
header = next(read_positions_file)
print(header)
