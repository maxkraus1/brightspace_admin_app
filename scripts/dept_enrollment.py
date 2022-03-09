"""Creates a csv enrollment report for a department in a given semester

Takes the Otis semester code as command line argument 1 and
Otis department code as argument 2
"""

import csv
import os
import sys

import datahub
import dwnld

sem_code = str(sys.argv[1])
dept_code = str(sys.argv[2])
semester = datahub.get_orgunit(dept_code)
department = datahub.get_orgunit(sem_code)

filename = sem_code + "_" + dept_code + ".csv"
path = datahub.REPORT_PATH
report = os.path.join(path, filename)
descendants = datahub.get_descendants(department, semester)
dept_sheet = datahub.dept_sheet(descendants)

courses = []
for row in dept_sheet[0]:
    if row["Type"] == "Course Offering":
        courses.append(
            {"OrgUnitId": row["OrgUnitId"],
            "CourseName": row["Name"],
            "CourseCode": row["Code"]
            })

full_rows = []
for row in courses:
    try:
        enrollments = dwnld.get_classlist(row["OrgUnitId"])
        for e in enrollments:
            new_row = {}
            new_row.update(row)
            new_row["UserId"] = e["Identifier"]
            new_row["Username"] = e["Username"]
            new_row["FirstName"] = e["FirstName"]
            new_row["LastName"] = e["LastName"]
            new_row["Email"] = e["Email"]
            new_row["Role"] = datahub.get_role(e["RoleId"])
            full_rows.append(new_row)
    except:
        continue

headers = ["OrgUnitId", "CourseName", "CourseCode", "UserId", "Username",
    "FirstName", "LastName", "Email", "Role"]
with open(report, "w", newline="") as outfile:
    writer = csv.DictWriter(outfile, fieldnames=headers)
    writer.writeheader()
    for row in full_rows:
        writer.writerow(row)
