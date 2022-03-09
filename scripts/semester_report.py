"""Creates an Excel report for the semester's course offering info

Takes school semester code as command line argument 1
"""

import os
import re
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
    df.to_excel(writer, sheet_name=sheet_name, index=False)
    worksheet = writer.sheets[sheet_name]
    worksheet.set_column('B:B', 70)
    worksheet.set_column('C:D', 13)
    worksheet.set_column('E:H', 18)

def main():
    courses = pd.DataFrame(datahub.get_semester_courses(sem))
    courses = courses.filter(items=["OrgUnitId", "Name", "Code"])
    dept_index = datahub.dept_index()
    instructors = datahub.instructor_index()
    counts = datahub.stud_enroll_index()
    contentobjs = datahub.content_obj_counts()
    df = courses.join(dept_index, on="OrgUnitId")
    df = df.merge(instructors, how="left", on="OrgUnitId")
    df = df.merge(counts, how="left", on="OrgUnitId")
    df = df.merge(contentobjs, how="left", on="OrgUnitId")
    df.sort_values(['DeptCode', 'Name'], inplace=True)  # Sort by Course Name
    format_sheet(df, "SemesterReport")
    if sem_code[-1] == '0':
        df2 = df.loc[df.Name.str.contains(r"X[A-Z]{3}")]
        format_sheet(df2, "Concurrent")
    writer.save()

if __name__ == "__main__":
    main()
    print('Report saved at ', name)
