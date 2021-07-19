"""Retrieves the Roster for each class in a csv file and outputs an Excel file

Takes a csv file of classes as command line argument 1 and the report filename
as argument 2
"""

import csv
import re
import sys

import pandas as pd

import dwnld

classlist = sys.argv[1]
path = "G:/Shared drives/~ LMS Brightspace Implementation/Data Hub"
filename = "{}/Reports/{}.xlsx".format(path, sys.argv[2])
role_details = path + "/Data Sets/RoleDetails.csv"

writer = pd.ExcelWriter(filename)
workbook = writer.book
title_format = workbook.add_format({"bold": True,
                                "font_color": "#4D9C34",
                                "font_size": 16})

with open(classlist, newline="", encoding="utf-8-sig") as infile:
    reader = csv.DictReader(infile)
    for row in reader:
        roster = dwnld.get_classlist(row["OrgUnitId"])
        for user in roster:
            with open(role_details,newline="",encoding="utf-8-sig") as rfile:
                roles = csv.DictReader(rfile, delimiter=",")
                for role in roles:
                    if str(user["RoleId"]) == role["RoleId"]:
                        user["Role"] = role["RoleName"]

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
