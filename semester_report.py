"""Creates an Excel report with one sheet for each department's org unit info

Takes Otis semester code as command line argument 1
"""

import os
import sys
import pandas as pd
import datahub

report_path = os.path.join(datahub.REPORT_PATH, "Semester Course Reports")
sem_code = str(sys.argv[1])
datahub.cross_listed(sem_code) # create cross-listed csv report
sem = datahub.get_orgunit(sem_code)
code_list = os.path.join(datahub.DATA_PATH, "BFA-MFACodes.txt")
filename = sem_code + "_SemesterReport.xlsx"
name = os.path.join(report_path, filename)

writer = pd.ExcelWriter(name)

with open(code_list) as f:
    for i in f.readlines():
        dept = i.rstrip()
        descendants = datahub.get_descendants(dept, sem)
        dept_code = datahub.get_code(dept)
        sheet = datahub.dept_sheet(descendants)
        df = pd.DataFrame(sheet[0], columns=sheet[1])
        df.sort_values(['Name'], inplace=True)  # Sort by Course Name
        df.to_excel(writer, sheet_name=dept_code, index=False)

        # format columns for Type, Name, and Code
        worksheet = writer.sheets[dept_code]
        worksheet.set_column('C:C', 16)
        worksheet.set_column('D:D', 69)
        worksheet.set_column('E:E', 13)
writer.save()
