"""Retrieves the Roster for each class in a csv file and outputs an Excel file

Takes the semester code as argument 1 and department code as argument 2
"""

import csv
import re
import os
import sys

import pandas as pd

import datahub
import dwnld

semester, department = sys.argv[1], sys.argv[2]
path = "G:/Shared drives/~ LMS Brightspace Implementation/Data Hub"
filename = os.path.join(datahub.REPORT_PATH,"{}_{}_Enrollment".format(
                                                        semester, department))
role_details = datahub.ROLE_DETAILS
sem_ou = datahub.get_orgunit(semester)
dept_ou = datahub.get_orgunit(department)

writer = pd.ExcelWriter(filename + ".xlsx")
workbook = writer.book
title_format = workbook.add_format({"bold": True,
                                "font_color": "#4D9C34",
                                "font_size": 16})

courses = datahub.dept_sheet(datahub.get_descendants(dept_ou, sem_ou))

for row in courses[0]:
    roster = dwnld.get_classlist(row["OrgUnitId"])
    for user in roster:
        user["Role"] = datahub.get_role(user["RoleId"])

    result = re.search(r"\((.+)\)", row["Name"])  # get course code from Name
    code = result.group(1)
    columns = ["FirstName", "LastName", "Username", "Email", "Role"]
    df = pd.DataFrame(roster, columns=columns)
    df.sort_values(['LastName'], inplace=True)  # Sort by Last Name
    df.to_excel(writer, sheet_name=code, startrow=2, index=False)

    # format columns
    worksheet = writer.sheets[code]
    worksheet.write(0,0, row['Name'], title_format)
    worksheet.write(1,0, "CRN: {}".format(row["Code"][:5]), title_format)
    worksheet.set_column('A:A', 15)
    worksheet.set_column('B:B', 15)
    worksheet.set_column('C:C', 12)
    worksheet.set_column('D:D', 25)
    worksheet.set_column('E:E', 20)

writer.save()
