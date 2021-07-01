"""Creates an Excel report for the semester's course offering info

Takes Otis semester code as command line argument 1
"""

import os
import sys
import pandas as pd
import datahub

report_path = os.path.join(datahub.REPORT_PATH, "Semester Course Reports")
sem_code = str(sys.argv[1])
sem = datahub.get_orgunit(sem_code)
filename = sem_code + "_SemesterReport.xlsx"
name = os.path.join(report_path, filename)
writer = pd.ExcelWriter(name)

def format_sheet(df, sheet_name):
    """"""
    df.drop(columns=["Organization", "Type", "IsDeleted", "DeletedDate",
                "RecycledDate", "Version", "OrgUnitTypeId"],
            inplace=True)
    df.sort_values(['Name'], inplace=True)  # Sort by Course Name
    df.to_excel(writer, sheet_name=sheet_name, index=False)
    worksheet = writer.sheets[sheet_name]
    worksheet.set_column('B:B', 70)
    worksheet.set_column('C:C', 13)

def bfa_mfa():
    """Produces a report for BFA/MFA semester with one department per tab"""
    datahub.cross_listed(sem) # create cross-listed csv report
    code_list = os.path.join(datahub.DATA_PATH, "BFA-MFACodes.txt")
    with open(code_list) as f:
        for i in f.readlines():
            dept = i.rstrip()
            descendants = datahub.get_descendants(dept, sem)
            dept_code = datahub.get_code(dept)
            sheet = datahub.dept_sheet(descendants)
            df = pd.DataFrame(sheet[0], columns=sheet[1])
            format_sheet(df, dept_code)

def extension():
    """produces a report with all course offerings in an extension semester"""
    courses = datahub.get_semester_courses(sem)
    fieldnames = courses[0].keys()
    df = pd.DataFrame(courses, columns=fieldnames)
    format_sheet(df, sem_code)

if __name__ == "__main__":
    if sem_code[-1] != '0':
        extension()
    else:
        bfa_mfa()
    writer.save()
